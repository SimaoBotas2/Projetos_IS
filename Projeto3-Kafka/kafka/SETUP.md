# Setup do Projeto Kafka - TP3

## Pré-requisitos
- Docker & Docker Compose instalados
- Workspace aberto em VS Code com Dev Container (opcional, mas recomendado)

---

## 1. Arrancar os Containers

A partir da pasta `kafka/`:

```bash
docker compose -f .devcontainer/docker-compose-standalone.yml up -d
```

Isto arranca:
- **database**: PostgreSQL (porta 5433 no host, 5432 interno)
- **broker1**: Apache Kafka (porta 29092 externa, 9092 interna)
- **connect**: Kafka Connect (porta 8083)
- **command-line**: Container para correr comandos e a aplicação Java

Verificar status:
```bash
docker compose -f .devcontainer/docker-compose-standalone.yml ps
```

---

## 2. Entrar no Container `command-line`

```bash
docker compose -f .devcontainer/docker-compose-standalone.yml exec command-line bash
```

Todos os comandos seguintes correm **dentro deste container**.

---

## 3. Compilar o Projeto Maven

Dentro do container:

```bash
cd /workspace
mvn clean package -DskipTests
```

Isto gera `target/project3-jar-with-dependencies.jar` com todas as dependências (Kafka Streams, Kafka Clients, GSON, etc).

---

## 4. Criar Tópicos de Input (se não existirem)

```bash
kafka-topics.sh --bootstrap-server broker1:9092 --create --topic Purchases --partitions 1 --replication-factor 1 --if-not-exists
kafka-topics.sh --bootstrap-server broker1:9092 --create --topic Sales --partitions 1 --replication-factor 1 --if-not-exists
```

---

## 5. Registar os Kafka Connect Connectors

Dentro do container:

```bash
cd /workspace/config
./post_connectors.sh
```

Isto registra **13 conectores** (1 source + 12 sink). O script é idempotente — apaga os existentes antes de re-registar.

Verificar conectores:
```bash
curl http://connect:8083/connectors
```

---

## 6. Verificar Tópicos Kafka

```bash
kafka-topics.sh --bootstrap-server broker1:9092 --list
```

Deves ver: `Purchases`, `Sales`, e todos os `Results-*` topics.

---

## 7. Correr Producers

Dentro do container, após compilação:

```bash
# Producer de compras (loop contínuo)
java -cp target/project3-jar-with-dependencies.jar is.project3.PurchaseEventProducer

# Producer de vendas (loop contínuo)
java -cp target/project3-jar-with-dependencies.jar is.project3.SaleEventProducer
```

Alternativamente, usa as MCP tools (`create_purchase_event`, `create_sale_event`) via agente IA.

---

## 8. Correr Kafka Streams

Dentro do container:

```bash
java -jar target/project3-jar-with-dependencies.jar is.project3.ProjetoBase3Streams
```

Ou em background:
```bash
java -jar target/project3-jar-with-dependencies.jar > /tmp/streams.log 2>&1 &
```

---

## 9. Verificar Dados no PostgreSQL

Dentro do container (ou no host na porta 5433):

```bash
psql -U postgres -d project3 -c "SELECT * FROM revenue_by_book;"
psql -U postgres -d project3 -c "SELECT * FROM total_metrics;"
psql -U postgres -d project3 -c "SELECT * FROM time_window_metrics;"
```

---

## 10. Consumir Mensagens (Verificação)

```bash
# Ver eventos de venda
kafka-console-consumer.sh --bootstrap-server broker1:9092 --topic Sales --from-beginning

# Ver resultados Kafka Streams (formato schema+payload JSON)
kafka-console-consumer.sh --bootstrap-server broker1:9092 --topic Results-revenue-per-book --from-beginning
```

---

## 11. Parar os Containers

Fora do container (no host):

```bash
cd kafka
docker compose -f .devcontainer/docker-compose-standalone.yml down
```

---

## 12. Reset Completo (Volumes Incluídos)

```bash
cd kafka
docker compose -f .devcontainer/docker-compose-standalone.yml down -v
```

Isto apaga todos os dados do PostgreSQL e offsets do Kafka.

---

## Troubleshooting

**Erro: `connect:8083 refused`**
→ Verifica se estás dentro do container `command-line` (não no host Windows).

**Connector em estado FAILED**
```bash
# Ver erro
curl http://connect:8083/connectors/<nome>/status

# Reiniciar task do connector
curl -X POST http://connect:8083/connectors/<nome>/tasks/0/restart
```

**Re-registar todos os connectors**
```bash
cd /workspace/config && ./post_connectors.sh
```

**Reset do consumer group (re-processar desde o início)**
```bash
kafka-consumer-groups.sh --bootstrap-server broker1:9092 \
  --group project3-analytics-streams \
  --reset-offsets --to-earliest \
  --topic Sales --topic Purchases --execute
```

**Limpar tópicos Results-* com mensagens antigas**
```bash
for topic in Results-revenue-per-book Results-expenses-per-book Results-profit-per-book \
  Results-avg-purchase-per-book Results-avg-purchase-all Results-total-revenue \
  Results-total-expenses Results-total-profit Results-top-profit-book \
  Results-revenue-last-hour Results-expenses-last-hour Results-top-country-sales-per-book; do
  kafka-topics.sh --bootstrap-server broker1:9092 --delete --topic $topic
done
```
