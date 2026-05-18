# Next Session — Testing Checklist

## Before Anything: Start the Stack

```bash
# Terminal 1 (Windows host) — start Docker
cd kafka
docker compose -f .devcontainer/docker-compose-standalone.yml up -d

# Wait ~30s for Kafka Connect to be healthy, then:
docker exec devcontainer-command-line-1 bash -c "cd /workspace/config && bash post_connectors.sh"

# Start Kafka Streams in background
docker exec -d devcontainer-command-line-1 bash -c "java -jar /workspace/target/project3-jar-with-dependencies.jar > /tmp/streams.log 2>&1"
```

```bash
# Terminal 2 (Windows host) — start Python API
cd api
.venv\Scripts\activate
python main.py        # REST API on :8001
```

---

## Step 1 — Verify PostgreSQL Has Data

```bash
docker exec devcontainer-database-1 psql -U postgres -d project3 -c "
SELECT 'revenue_by_book'           AS tbl, COUNT(*) FROM revenue_by_book
UNION ALL SELECT 'expenses_by_book',        COUNT(*) FROM expenses_by_book
UNION ALL SELECT 'profit_by_book',          COUNT(*) FROM profit_by_book
UNION ALL SELECT 'total_metrics',           COUNT(*) FROM total_metrics
UNION ALL SELECT 'time_window_metrics',     COUNT(*) FROM time_window_metrics
UNION ALL SELECT 'best_performing_by_country', COUNT(*) FROM best_performing_by_country;
"
```

**Expected**: all tables have rows.  
**If empty**: send test events (see Step 2), wait 10s, re-check.

Check `total_metrics` specifically — it should have 5 rows:

```bash
docker exec devcontainer-database-1 psql -U postgres -d project3 -c "SELECT * FROM total_metrics;"
```

**Expected rows**: `total_revenue`, `total_expenses`, `total_profit`, `top_profit_book`, `average_purchase`  
**Last session**: only 3 appeared (total_profit and average_purchase were missing — needs more events to trigger the KTable joins)

---

## Step 2 — Send Test Events (if needed)

```bash
NOW=$(date +%s%3N)

# Sales (book_id, country_id, price, quantity)
for i in 1 2 3; do
  echo "{\"book_id\":1,\"country_id\":1,\"price\":15.00,\"quantity\":2,\"timestamp\":$NOW}" | \
    docker exec -i devcontainer-command-line-1 kafka-console-producer.sh \
    --bootstrap-server broker1:9092 --topic Sales 2>/dev/null
  echo "{\"book_id\":2,\"country_id\":2,\"price\":22.00,\"quantity\":1,\"timestamp\":$NOW}" | \
    docker exec -i devcontainer-command-line-1 kafka-console-producer.sh \
    --bootstrap-server broker1:9092 --topic Sales 2>/dev/null
done

# Purchases (book_id, supplier_id, cost, quantity) — supplier_id is optional but include it
for i in 1 2 3; do
  echo "{\"book_id\":1,\"supplier_id\":1,\"cost\":10.00,\"quantity\":2,\"timestamp\":$NOW}" | \
    docker exec -i devcontainer-command-line-1 kafka-console-producer.sh \
    --bootstrap-server broker1:9092 --topic Purchases 2>/dev/null
  echo "{\"book_id\":2,\"supplier_id\":1,\"cost\":15.00,\"quantity\":1,\"timestamp\":$NOW}" | \
    docker exec -i devcontainer-command-line-1 kafka-console-producer.sh \
    --bootstrap-server broker1:9092 --topic Purchases 2>/dev/null
done
```

Wait 10–15 seconds, then re-check PostgreSQL.

---

## Step 3 — Test REST API Endpoints

Base URL: `http://127.0.0.1:8001`

### CRUD

```bash
# List books
curl http://127.0.0.1:8001/books

# List countries
curl http://127.0.0.1:8001/countries

# List authors
curl http://127.0.0.1:8001/authors
```

### Analytics — Per Book

```bash
curl http://127.0.0.1:8001/analytics/stats/revenue-per-book
curl http://127.0.0.1:8001/analytics/stats/expenses-per-book
curl http://127.0.0.1:8001/analytics/stats/profit-per-book
curl http://127.0.0.1:8001/analytics/stats/avg-purchase-per-book
```

### Analytics — Totals

```bash
curl http://127.0.0.1:8001/analytics/stats/total-revenue
curl http://127.0.0.1:8001/analytics/stats/total-expenses
curl http://127.0.0.1:8001/analytics/stats/total-profit
curl http://127.0.0.1:8001/analytics/stats/avg-purchase-all
curl http://127.0.0.1:8001/analytics/stats/top-profit-book
```

### Analytics — Windowed

```bash
curl http://127.0.0.1:8001/analytics/stats/revenue-last-hour
curl http://127.0.0.1:8001/analytics/stats/expenses-last-hour
```

### Analytics — Country

```bash
curl http://127.0.0.1:8001/analytics/stats/top-country-sales-per-book
```

### Dashboard (all at once)

```bash
curl http://127.0.0.1:8001/analytics/stats/dashboard
```

**For each**: expect a JSON response with actual numbers, not `null` or `[]`.  
**If 500 error**: check the exact endpoint name in `api/main.py` — the route paths may differ slightly.

---

## Step 4 — Test MCP Agent

```bash
# Terminal 3 — MCP Server
cd api && python mcp_server.py   # runs on :8002

# Terminal 4 — Agent
cd api && python langchain_agent.py   # runs on :8000
```

Open `api/webapp.html` in browser and try:

| Ask the agent | Expected tool called |
|---|---|
| "List all countries" | `list_countries_tool` |
| "Add country Italy, region Europe" | `create_country_tool` |
| "List all books" | `list_books_tool` |
| "What is the total revenue?" | `get_total_revenue_tool` |
| "Show me revenue per book" | `get_revenue_per_book_tool` |
| "What book has the highest profit?" | `get_top_profit_book_tool` |
| "Generate 5 test transactions" | `create_test_transactions` |
| "What is the revenue in the last hour?" | `get_revenue_last_hour_tool` |
| "Which country has the highest sales for book 1?" | `get_top_country_sales_per_book_tool` |

---

## Step 5 — Check Connector Health

If any API endpoint returns empty/null, check the corresponding connector:

```bash
# Check all connector statuses
docker exec devcontainer-command-line-1 bash -c "
for conn in \$(curl -s http://connect:8083/connectors | tr '[]\",' '\n' | grep jdbc); do
  state=\$(curl -s http://connect:8083/connectors/\$conn/status | grep -o '\"state\":\"[^\"]*\"' | head -1)
  echo \"\$conn: \$state\"
done
"

# Restart any FAILED tasks
docker exec devcontainer-command-line-1 bash -c "
for conn in \$(curl -s http://connect:8083/connectors | tr '[]\",' '\n' | grep jdbc-sink); do
  curl -s -X POST http://connect:8083/connectors/\$conn/tasks/0/restart
done
echo 'All tasks restarted'
"
```

---

## Known Issues Going In

| Issue | Where | Impact |
|---|---|---|
| `total_profit` and `average_purchase` may be missing from `total_metrics` | Kafka Streams KTable join needs both Sales+Purchases events | Fix: send more events |
| REST API endpoint paths not verified | `api/main.py` | May need to check exact route names |
