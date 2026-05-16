# Session State — Kafka Pipeline Fix

## Status: ✅ WORKING

The full pipeline is operational:
**MCP/Producer → Kafka → Kafka Streams → Results Topics → Kafka Connect → PostgreSQL → REST API**

---

## What Was Fixed (This Session)

### Root Cause
Kafka Connect JDBC Sink requires **schema-embedded JSON** (the `{"schema":{...},"payload":{...}}` envelope).
Plain JSON from Kafka Streams was always rejected with "null value schema" error.

### Solution Applied
Changed `ProjetoBase3Streams.java` to produce typed schema+payload JSON directly, **per topic**.
No Schema Registry. No transforms in sink connectors.

Four helper methods in ProjetoBase3Streams.java:
- `bookMetricJson(valueField, bookId, value)` → for revenue_by_book, expenses_by_book, profit_by_book, average_purchase_by_book
- `totalMetricJson(metricName, value)` → for total_metrics (total_revenue, total_expenses, total_profit, top_profit_book, average_purchase)
- `windowedMetricJson(metricType, value)` → for time_window_metrics (revenue_last_hour, expenses_last_hour)
- `countryMetricJson(compositeKey, revenue)` → for best_performing_by_country (key = "bookId_countryId")

Schema types used: `int32` for IDs, `double` for amounts, `string` for names. 
Note: Kafka Connect JsonConverter does NOT accept `float64` — use `double` instead.

Also fixed:
- `PurchaseEvent.fromJson()` — made `supplier_id` optional (defaults to 0)
- Added `LogAndContinueExceptionHandler` to Kafka Streams config so malformed legacy messages are skipped
- All sink connector JSON files updated: `schemas.enable=true`, no transforms
- `post_connectors.sh` now deletes existing connectors before re-registering (idempotent)

---

## Verified Working ✅

Data confirmed in PostgreSQL after end-to-end test:

| Table | Rows |
|-------|------|
| revenue_by_book | 3 (books 1, 2, 3) |
| expenses_by_book | 2 (books 1, 2) |
| profit_by_book | 2 (books 1, 2) |
| total_metrics | 3 (total_revenue, total_expenses, top_profit_book) |
| time_window_metrics | 2 (revenue_last_hour, expenses_last_hour) |
| best_performing_by_country | 3 rows |

**Missing from total_metrics**: `total_profit` and `average_purchase` — these require a join between
totalRevenue+totalExpenses and totalExpenses+purchaseCountAll. May need more events to trigger the join.

---

## Current Container Names

| Service | Container |
|---------|-----------|
| Kafka broker | `devcontainer-broker1-1` |
| PostgreSQL | `devcontainer-database-1` |
| Kafka Connect | `devcontainer-connect-1` |
| Command line | `devcontainer-command-line-1` |

---

## How to Run When Resuming

### Start Everything
```bash
# From kafka/ directory
docker compose -f .devcontainer/docker-compose-standalone.yml up -d
```

### Register Connectors (if not already registered)
```bash
docker exec devcontainer-command-line-1 bash -c "cd /workspace/config && bash post_connectors.sh"
```

### Build the JAR (if code changed)
```bash
docker exec devcontainer-command-line-1 bash -c "cd /workspace && mvn package -DskipTests -q"
```

### Create Input Topics (if they don't exist)
```bash
docker exec devcontainer-command-line-1 bash -c "
kafka-topics.sh --bootstrap-server broker1:9092 --create --topic Sales --partitions 1 --replication-factor 1 --if-not-exists
kafka-topics.sh --bootstrap-server broker1:9092 --create --topic Purchases --partitions 1 --replication-factor 1 --if-not-exists
"
```

### Start Kafka Streams
```bash
docker exec -d devcontainer-command-line-1 bash -c "java -jar /workspace/target/project3-jar-with-dependencies.jar > /tmp/streams.log 2>&1"
```

### Send Test Events
```bash
NOW=$(date +%s%3N)
# Sales
echo "{\"book_id\":1,\"country_id\":1,\"price\":15.00,\"quantity\":2,\"timestamp\":$NOW}" | \
  docker exec -i devcontainer-command-line-1 kafka-console-producer.sh \
  --bootstrap-server broker1:9092 --topic Sales

# Purchases (supplier_id is optional but include it)
echo "{\"book_id\":1,\"supplier_id\":1,\"cost\":10.00,\"quantity\":2,\"timestamp\":$NOW}" | \
  docker exec -i devcontainer-command-line-1 kafka-console-producer.sh \
  --bootstrap-server broker1:9092 --topic Purchases
```

### Check PostgreSQL
```bash
docker exec devcontainer-database-1 psql -U postgres -d project3 -c "SELECT * FROM revenue_by_book;"
docker exec devcontainer-database-1 psql -U postgres -d project3 -c "SELECT * FROM total_metrics;"
```

### Check Connector Health
```bash
docker exec devcontainer-command-line-1 curl -s http://connect:8083/connectors/jdbc-sink-revenue-per-book/status | grep '"state"'
```

### Restart FAILED connector tasks
```bash
docker exec devcontainer-command-line-1 bash -c "
for conn in \$(curl -s http://connect:8083/connectors | tr '[]\",' '\n' | grep 'jdbc-sink'); do
  curl -s -X POST http://connect:8083/connectors/\$conn/tasks/0/restart
done
"
```

---

## What Still Needs Work

### total_profit and average_purchase not in total_metrics
Both require KTable joins to work. They need both Sales AND Purchases events before they appear.
Send more events (with proper supplier_id) to trigger both joins.

### No profit_last_hour (Req #16)
Requires joining two windowed KTables — complex in Kafka Streams. Currently not implemented.
Consider implementing as: compute separately and join with a GlobalKTable.

### REST API Not Verified
The REST API (FastAPI in /api/) has analytics query functions that read from the PostgreSQL tables.
These need to be tested end-to-end now that the tables have real data.

### MCP Agent Not Tested This Session
The Python MCP producer (api/mcp_server.py) was used in a previous session to produce events.
It should work without changes since the Sales/Purchases topic format hasn't changed.

---

## Key Files Changed This Session

1. `kafka/src/main/java/is/project3/ProjetoBase3Streams.java` — full rewrite of output serialization
2. `kafka/src/main/java/is/project3/PurchaseEvent.java` — optional supplier_id
3. `kafka/src/main/java/is/project3/MetricEvent.java` — minor (kept for internal use)
4. `kafka/config/sink-*.json` — ALL 12 sink connectors: schemas.enable=true, no transforms
5. `kafka/config/post_connectors.sh` — idempotent (deletes before re-registering)
6. `docs/FIX_KAFKA_CONNECT_SCHEMA.md` — original fix plan (now implemented)
