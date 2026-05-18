# Demo Roadmap

## Foco: Pipeline Kafka (o que é novo neste projeto)

---

### 1. Preparar o ambiente (antes de apresentar)

Arrancar o stack e os serviços Python:
```bash
cd kafka
docker compose -f .devcontainer/docker-compose-cluster.yml up -d
# aguardar ~60s

scripts\start_all.bat
```

Abrir o **Windows Terminal** com 2 painéis lado a lado (Ctrl+Shift+D):

**Painel esquerdo** — consumer a escutar o tópico Sales em tempo real:
```bash
docker exec devcontainer-command-line-1 kafka-console-consumer.sh \
  --bootstrap-server broker1:9092 --topic Sales
```

**Painel direito** — PostgreSQL a actualizar de 2 em 2 segundos:
```bash
docker exec devcontainer-database-1 watch -n 2 \
  'psql -U postgres -d project3 -c "SELECT * FROM total_metrics;"'
```

---

### 2. Mostrar a arquitectura (slide)

Referir brevemente: 3 brokers, Kafka Streams, 14 connectors, PostgreSQL.

---

### 3. Demonstração ao vivo

Abrir `api/webapp.html` no browser com os painéis visíveis em segundo plano.

Pedir ao agente:
> *"Generate 10 test transactions"*

Apontar para os terminais:
- **Painel esquerdo**: eventos a aparecer no Kafka em tempo real
- **Painel direito**: valores do `total_metrics` a mudar ~10s depois

---

### 4. Mostrar os connectors

```bash
curl -s http://localhost:8083/connectors | tr ',' '\n'
```

Explicar: **1 Source** (PostgreSQL → Kafka) e **13 Sinks** (Kafka → PostgreSQL), um por métrica — tudo configurado em JSON, sem código.

---

### 5. Fechar o loop — API reflecte os dados

```bash
curl -s http://127.0.0.1:8001/analytics/stats/dashboard
```

Mostrar que os valores na API são os mesmos que apareceram no PostgreSQL.

---

### 6. Perguntas ao agente (referência rápida — já demonstrado antes)

> *"What is the total revenue?"*
> *"Which book has the highest profit?"*
> *"Which country has the highest sales for book 1?"*

---

## Sequência resumida

```
Webapp (agente)
      ↓ create_test_transactions
   Kafka Topics  ← visível no painel esquerdo
      ↓
 Kafka Streams
      ↓
 Kafka Connect (13 sinks)
      ↓
  PostgreSQL    ← visível no painel direito (watch)
      ↓
  REST API / Agente
```
