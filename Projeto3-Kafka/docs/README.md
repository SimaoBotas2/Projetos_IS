# Projeto 3: Kafka Real-Time Event Processing

Sistema de processamento em tempo real de eventos de compras/vendas com Apache Kafka, exposto via REST API e agente IA (LangChain + MCP).

## Estrutura

```
Projeto3-Kafka/
├── kafka/      → Java: Kafka Streams, producers, Kafka Connect, Docker
├── api/        → Python: FastAPI REST API, MCP Server, LangChain Agent
├── docs/       → Documentação
└── scripts/    → start_all.bat (Windows)
```

---

## Como Correr

O projeto tem **duas partes independentes** — o lado Kafka (Java/Docker) e o lado API (Python).

---

### Parte 1 — Kafka (dentro do Docker)

```bash
# 1. Arrancar os containers
cd kafka
docker compose -f .devcontainer/docker-compose-standalone.yml up -d

# 2. Entrar no container de linha de comandos
docker compose -f .devcontainer/docker-compose-standalone.yml exec command-line bash

# --- Os comandos abaixo correm DENTRO do container ---

# 3. Registar os Kafka Connect connectors (Source + Sink)
cd /workspace/config
./post_connectors.sh

# 4. Compilar o projeto Maven (gera fat JAR com todas as dependências)
cd /workspace
mvn clean package

# 5. Correr os 3 componentes (cada um num terminal separado, ou usar run_streams.sh)
java -cp target/project3-jar-with-dependencies.jar is.project3.PurchaseEventProducer
java -cp target/project3-jar-with-dependencies.jar is.project3.SaleEventProducer
java -cp target/project3-jar-with-dependencies.jar is.project3.ProjetoBase3Streams

# Alternativa: correr tudo em background com script
./run_streams.sh
```

Verificar que está a funcionar:
```bash
# Ver tópicos Kafka
kafka-topics.sh --bootstrap-server broker1:9092 --list

# Ver resultados a chegar ao tópico Results
kafka-console-consumer.sh --bootstrap-server broker1:9092 --topic Results --from-beginning

# Ver dados no PostgreSQL
psql -U postgres -d project3 -c "SELECT * FROM analytics_results LIMIT 10;"
```

---

### Parte 2 — API Python (no host, fora do Docker)

```bash
# 1. Criar e ativar virtual environment (só na primeira vez)
cd api
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Correr os 3 serviços (cada um num terminal separado)
python main.py          # REST API     → http://127.0.0.1:8001
python mcp_server.py    # MCP Server   → http://127.0.0.1:8002/sse
python langchain_agent.py  # Agent API → http://127.0.0.1:8000
```

Abrir `api/webapp.html` no browser para aceder ao chat interface.

---

### Windows — Início Rápido

```bat
scripts\start_all.bat
```

Abre os 3 serviços Python em janelas separadas e lança a webapp no browser.  
> Requer `.venv` criado em `api/` previamente.

---

## Serviços e Portas

| Serviço | Porta | Descrição |
|---|---|---|
| REST API | `8001` | FastAPI — endpoints CRUD e analytics |
| MCP Server | `8002` | MCP SSE server — tools para o agente IA |
| Agent API | `8000` | LangChain Agent — recebe perguntas em linguagem natural |
| PostgreSQL | `5432` | Base de dados (dentro do Docker) |
| Kafka Broker | `9092` | Broker interno (dentro do Docker) |
| Kafka Connect | `8083` | Connectors REST API (dentro do Docker) |

---

## Métricas Calculadas pelo Kafka Streams

| Métrica | Tópico/Tabela | Requisito |
|---|---|---|
| Revenue por livro | `revenue_by_book` | #5 |
| Expenses por livro | `expenses_by_book` | #6 |
| Profit por livro | `profit_by_book` | #7 |
| Total revenue | `total_revenue` | #8 |
| Total expenses | `total_expenses` | #9 |
| Total profit | `total_profit` | #10 |
| Compra média por livro | `avg_purchase_by_book` | #11 |
| Compra média global | `avg_purchase_all` | #12 |
| Livro com maior lucro | `top_profit_book` | #13 |
| Revenue última hora | `revenue_last_hour` | #14 |
| Expenses última hora | `expenses_last_hour` | #15 |

---

## Parar Tudo

```bash
# Parar containers Docker
cd kafka
docker compose -f .devcontainer/docker-compose-standalone.yml down

# Limpar volumes também (reset completo)
docker compose -f .devcontainer/docker-compose-standalone.yml down -v
```
