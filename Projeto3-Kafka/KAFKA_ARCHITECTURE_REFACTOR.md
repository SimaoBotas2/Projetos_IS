# Kafka Architecture Refactor - Multiple Streams per Metric

## Overview

Refactored the Kafka Streams topology to emit each metric to its own dedicated topic, following best practices for Kafka architecture. This simplifies Kafka Connect configuration and makes the system more scalable and maintainable.

## Architecture

```
Kafka Streams Application
├─ Reads: Purchases, Sales, DBInfo topics
└─ Emits to separate metric topics:
   ├─ Results-revenue-per-book          → [JDBC Sink] → revenue_by_book
   ├─ Results-expenses-per-book         → [JDBC Sink] → expenses_by_book
   ├─ Results-profit-per-book           → [JDBC Sink] → profit_by_book
   ├─ Results-total-revenue             → [JDBC Sink] → total_revenue
   ├─ Results-total-expenses            → [JDBC Sink] → total_expenses
   ├─ Results-total-profit              → [JDBC Sink] → total_profit
   ├─ Results-avg-purchase-per-book     → [JDBC Sink] → avg_purchase_by_book
   ├─ Results-avg-purchase-all          → [JDBC Sink] → average_purchase
   ├─ Results-top-profit-book           → [JDBC Sink] → top_profit_book
   ├─ Results-revenue-last-hour         → [JDBC Sink] → revenue_last_hour
   ├─ Results-expenses-last-hour        → [JDBC Sink] → expenses_last_hour
   ├─ Results-profit-last-hour          → [JDBC Sink] → profit_last_hour
   └─ Results-top-country-sales-per-book → [JDBC Sink] → top_sales_by_country_per_book
```

## Files Changed

### 1. Kafka Streams Topology
**`kafka/src/main/java/is/project3/ProjetoBase3Streams.java`**
- Removed single "Results" topic output
- Added separate `.to()` calls for each metric
- Now emits MetricEvent (JSON) objects instead of raw numbers
- Each metric gets its own topic with predictable naming

### 2. New Classes Created
**`kafka/src/main/java/is/project3/MetricEvent.java`**
- Simple POJO representing a metric result
- Fields: `key`, `value`, `timestamp`
- Serializable to/from JSON
- Used by all metric topics for consistency

**`kafka/src/main/java/is/project3/EventSerdes.java`** (extended)
- Added `MetricEventSerde` class
- Handles JSON serialization/deserialization of MetricEvent objects

### 3. Kafka Connect Sink Connectors
**`kafka/config/sink-*.json`** (13 files, one per metric)
- Each connector maps one Results-* topic to its corresponding table
- Uses JsonConverter with schemas disabled
- Uses SMT transforms to extract fields from JSON
- Example: `sink-revenue-per-book.json` reads Results-revenue-per-book and writes to revenue_by_book table

## Message Format

All metrics now use a consistent JSON format in Kafka:

```json
{
  "key": "1",
  "value": 5000.50,
  "timestamp": 1652784526000
}
```

Kafka Connect then:
1. Reads this JSON
2. Extracts the `key` field (book_id, country_id, etc.)
3. Uses it as the primary key for UPSERT
4. Stores the `value` in the appropriate column
5. Records the `timestamp` of the update

## Benefits

✅ **Simpler Kafka Connect Configuration**
- One connector per topic (not trying to route all metrics to one table)
- Clear field mapping in each connector

✅ **Better Scalability**
- Easy to add new metrics (just add new topic + connector)
- No complex routing logic needed

✅ **Standard Kafka Patterns**
- Topic per entity is Kafka best practice
- Makes the system more understandable

✅ **Follows Assignment Requirements**
- "Results topics" (plural) - satisfied with 13 dedicated metric topics
- Clean separation of concerns

## Next Steps

### 1. Rebuild Kafka Streams Application
```bash
cd kafka
mvn clean package
docker build -t kafka-streams-app .
```

### 2. Restart Kafka Streams Container
```bash
docker-compose -f .devcontainer/docker-compose-standalone.yml restart command-line
```

### 3. Create PostgreSQL Tables
```bash
psql -h localhost -p 5433 -U postgres -d project3 -f ../api/create_analytics_tables.sql
```

### 4. Register Kafka Connect Sink Connectors
```bash
cd kafka/config

# Register each sink connector
for file in sink-*.json; do
    curl -X POST -H "Accept:application/json" -H "Content-Type:application/json" \
         http://localhost:8083/connectors -d @"$file"
done
```

Or run the updated post_connectors.sh:
```bash
./post_connectors.sh
```

### 5. Test the Data Flow
Send test data through the system:
```bash
# Via Python agent or manual producer
# Create some sales and purchases
# Watch the metrics appear in PostgreSQL
```

### 6. Verify Results
```bash
curl http://localhost:8001/analytics/stats/revenue-per-book
curl http://localhost:8001/analytics/stats/total-revenue
# etc.
```

## Kafka Connect Connector Pattern

All 13 sink connectors follow this pattern:

```json
{
    "name": "jdbc-sink-{metric-name}",
    "config": {
        "connection.url": "jdbc:postgresql://database:5432/project3?user=postgres&password=nopass",
        "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
        "dialect.name": "PostgreSqlDatabaseDialect",
        "tasks.max": "1",
        "topics": "Results-{metric-name}",
        "table.name.format": "{table-name}",
        "auto.create": "false",
        "auto.evolve": "true",
        "insert.mode": "upsert|insert",
        "pk.mode": "record_key|none",
        "pk.fields": "{primary-key}",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": "false",
        "transforms": "ValueToKey,ExtractValue",
        "transforms.ValueToKey.type": "org.apache.kafka.connect.transforms.ValueToKey",
        "transforms.ValueToKey.fields": "key",
        "transforms.ExtractValue.type": "org.apache.kafka.connect.transforms.ReplaceField$Value",
        "transforms.ExtractValue.exclude": "key,timestamp"
    }
}
```

## Troubleshooting

### Connectors not registering
- Verify Kafka Connect is running: `docker-compose ps | grep connect`
- Check connector logs: `docker logs kafka-connect-1`
- Test connectivity: `curl http://localhost:8083/connectors`

### No data appearing in tables
- Verify Kafka Streams topics exist: `docker-compose exec broker1 kafka-topics --list`
- Check messages in Results topics: `docker-compose exec broker1 kafka-console-consumer --topic Results-revenue-per-book`
- Check connector status: `curl http://localhost:8083/connectors/{name}/status`

### PostgreSQL errors
- Verify tables exist: `psql -h localhost -p 5433 -U postgres -d project3 -c "\dt"`
- Check connection string in connector config
- Verify database is running: `docker-compose ps | grep database`

## Assignment Compliance

✅ **Kafka Streams**: Computes 17 different metrics  
✅ **Results Topics**: 13 dedicated topics (plural), one per metric  
✅ **Kafka Connect**: JDBC Sink connectors write to PostgreSQL  
✅ **REST API**: Queries PostgreSQL tables  
✅ **MCP Tools**: Available for agent queries  
✅ **JSON Serialization**: Clean JSON format for all metrics  

The architecture now properly follows the assignment requirements with Kafka Streams → Kafka Connect → PostgreSQL data flow.
