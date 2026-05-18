# How to Run

## 1. Clean Start (reset everything)

```bash
cd kafka
docker compose -f .devcontainer/docker-compose-cluster.yml down -v
```

---

## 2. Start the Stack

```bash
docker compose -f .devcontainer/docker-compose-cluster.yml up -d
```

Wait ~60s, then verify Kafka Connect is ready:
```bash
curl -s http://localhost:8083/connectors
```
Should return `[]`.

---

## 3. Build (if needed)

```bash
docker exec devcontainer-command-line-1 bash -c "cd /workspace && mvn clean package -DskipTests -q"
```

---

## 4. Register Connectors

```bash
docker exec devcontainer-command-line-1 bash -c "sed -i 's/\r//' /workspace/config/post_connectors.sh && cd /workspace/config && bash post_connectors.sh"
```

Should print `✓ OK` for all 14 connectors.

---

## 5. Create Input Topics

```bash
docker exec devcontainer-command-line-1 bash -c "
kafka-topics.sh --create --if-not-exists --bootstrap-server broker1:9092 --topic Sales --partitions 3 --replication-factor 3
kafka-topics.sh --create --if-not-exists --bootstrap-server broker1:9092 --topic Purchases --partitions 3 --replication-factor 3
"
```

---

## 6. Start Kafka Streams

```bash
docker exec -d devcontainer-command-line-1 bash -c "java -jar /workspace/target/project3-jar-with-dependencies.jar > /tmp/streams.log 2>&1"
```

---

## 7. Start Python API

```bat
scripts\start_all.bat
```

---

## 8. Verify Everything is Working

```bash
docker exec devcontainer-database-1 psql -U postgres -d project3 -c "SELECT * FROM total_metrics;"
```

If empty, send test events and wait ~15s:
```bash
docker exec -it devcontainer-command-line-1 bash -c "
NOW=\$(date +%s%3N)
for i in 1 2 3; do
  echo '{\"book_id\":1,\"country_id\":1,\"price\":15.00,\"quantity\":2,\"timestamp\":'\$NOW'}' | kafka-console-producer.sh --bootstrap-server broker1:9092 --topic Sales 2>/dev/null
  echo '{\"book_id\":2,\"country_id\":2,\"price\":22.00,\"quantity\":1,\"timestamp\":'\$NOW'}' | kafka-console-producer.sh --bootstrap-server broker1:9092 --topic Sales 2>/dev/null
  echo '{\"book_id\":1,\"supplier_id\":1,\"cost\":10.00,\"quantity\":2,\"timestamp\":'\$NOW'}' | kafka-console-producer.sh --bootstrap-server broker1:9092 --topic Purchases 2>/dev/null
  echo '{\"book_id\":2,\"supplier_id\":2,\"cost\":15.00,\"quantity\":1,\"timestamp\":'\$NOW'}' | kafka-console-producer.sh --bootstrap-server broker1:9092 --topic Purchases 2>/dev/null
done
"
```

---

## 9. Stop

```bash
docker compose -f .devcontainer/docker-compose-cluster.yml down
```
