# Projeto 3: Kafka Real-Time Event Processing

## Visão Geral

Sistema de processamento em tempo real de eventos de vendas e compras usando Apache Kafka. Processa eventos com Kafka Streams, persiste em PostgreSQL via Kafka Connect, e expõe resultados através de REST API com integração a IA (LangChain + MCP).

**Objetivo**: Demonstrar integração end-to-end de componentes de sistemas distribuídos (brokers, streaming, persistence, APIs).

## Arquitetura

```
Producers                Kafka Topics            Streams Processing        Persistence
┌──────────────────┐     ┌──────────────────┐   ┌──────────────────┐     ┌─────────────┐
│ Purchase Events  │────▶│ Purchases Topic  │──▶│                  │────▶│             │
│ Sale Events      │     │ Sales Topic      │   │ Kafka Streams    │     │ PostgreSQL  │
└──────────────────┘     └──────────────────┘   │ (11+ metrics)    │     │ (Results)   │
                                                 └──────────────────┘     └─────────────┘
                                                           │
                         ┌─────────────────────────────────┘
                         ▼
                 ┌──────────────────┐
                 │ Results Topic    │◀─┐
                 └──────────────────┘  │
                         │              │
                    Kafka Connect───────┘
                         │
                    REST API (FastAPI)
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
        Web Dashboard         LangChain Agent (IA)
```

## Tech Stack

**Backend**
- Java 16, Maven 3.8.1
- Apache Kafka 2.8.1 (broker)
- Kafka Streams 2.8.1 (processing)
- Kafka Connect (persistence layer)
- PostgreSQL 13
- GSON (serialization)

**Frontend/API**
- Python 3.8+, FastAPI 0.135.1
- SQLModel (ORM)
- LangChain 1.2.12 + Google GenAI
- MCP 1.26.0 (Model Context Protocol)
- Uvicorn (ASGI server)

**Infraestrutura**
- Docker & Docker Compose
- Dev Containers (VS Code)

## Componentes Principais

| Componente | Descrição | Tecnologia |
|---|---|---|
| **Producers** | Geram eventos de compra/venda com dados realistas | Java + Javafaker |
| **Streams** | Processa 11+ métricas: receita, despesas, lucro, top books/países | Kafka Streams |
| **Connectors** | Sincroniza config DB → Kafka e resultados Kafka → PostgreSQL | Kafka Connect JDBC |
| **REST API** | Consulta resultados de análises | FastAPI |
| **Web App** | Dashboard interativo com agente IA | HTML/CSS + LangChain |

## Como Executar

### Início Rápido

```bash
# 1. Iniciar containers (Docker Compose)
cd TP3-base/.devcontainer
docker compose -f docker-compose-standalone.yml up -d

# 2. Entrar no container de linha de comando
docker compose -f docker-compose-standalone.yml exec command-line bash

# 3. Setup (dentro do container)
cd /workspace/config && ./post_connectors.sh
mvn clean package

# 4. Executar producers e streams (em terminais separados)
java -cp target/project3-0.0.1-SNAPSHOT.jar PurchaseEventProducer
java -cp target/project3-0.0.1-SNAPSHOT.jar SaleEventProducer
java -cp target/project3-0.0.1-SNAPSHOT.jar ProjetoBase3Streams

# 5. Acessar API
# REST API: http://localhost:8001
# Web App: http://localhost:8001/webapp
```

**Veja [SETUP.md](TP3-base/SETUP.md) para instruções detalhadas.**

## Database Schema

**Tabelas de Configuração** (sincronizadas via Kafka Connect Source)
- `suppliers` (5 fornecedores)
- `countries` (5 países: Portugal, Spain, France, Germany, Brazil)
- `books` (5 livros clássicos com preços)

**Tabelas de Resultados** (preenchidas via Kafka Connect Sink)
- `analytics_results` (métrica genérica com timestamp)
- `revenue_by_book`, `expenses_by_book`, `profit_by_book` (agregados específicos)
- `average_purchase_by_book` (custos médios)
- `time_window_metrics` (análises por janelas de 1h)
- `best_performing_by_country` (top performing livro por país)

## Verificação

```bash
# Listar tópicos Kafka
kafka-topics.sh --bootstrap-server broker1:9092 --list

# Consumir eventos (ex: Purchases)
kafka-console-consumer.sh --bootstrap-server broker1:9092 --topic Purchases

# Verificar dados no PostgreSQL (dentro do container database)
psql -U postgres -d project3 -c "SELECT COUNT(*) FROM analytics_results;"
```

## Parar

```bash
cd TP3-base/.devcontainer
docker compose -f docker-compose-standalone.yml down
```

## Estrutura do Projeto

```
Projeto3-Kafka/
├── TP3-base/                    # Backend Java + Kafka
│   ├── src/main/java/is/project3/
│   │   ├── ProjetoBase3Streams.java    # Aplicação Streams
│   │   ├── PurchaseEventProducer.java  # Producer de compras
│   │   ├── SaleEventProducer.java      # Producer de vendas
│   │   └── models/                     # Event models (GSON)
│   ├── sql/create_tables.sql           # Schema PostgreSQL
│   ├── config/post_connectors.sh       # Setup Kafka Connect
│   ├── .devcontainer/docker-compose-standalone.yml
│   ├── pom.xml
│   └── SETUP.md
├── ProjetoBase_MCP_Agent_Web/  # Frontend Python + IA
│   ├── app/
│   │   ├── main.py             # REST API (FastAPI)
│   │   ├── mcp_server.py       # MCP SSE server
│   │   ├── langchain_agent.py  # Agent IA
│   │   └── models.py, services.py
│   ├── webapp.html             # Dashboard
│   └── requirements.txt
└── README.md (este arquivo)
```

---

**Contato/Issues**: Veja SETUP.md para troubleshooting detalhado.
