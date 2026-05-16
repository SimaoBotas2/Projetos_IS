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

## Serviços e Portas

| Serviço | Porta | Descrição |
|---|---|---|
| REST API | `8001` | FastAPI — endpoints CRUD e analytics |
| MCP Server | `8002` | MCP SSE server — tools para o agente IA |
| Agent API | `8000` | LangChain Agent — recebe perguntas em linguagem natural |
| PostgreSQL | `5433` | Base de dados (Docker → host: 5433, interno: 5432) |
| Kafka Broker | `29092` | Broker externo (host); `9092` interno (dentro do Docker) |
| Kafka Connect | `8083` | Connectors REST API (dentro do Docker) |

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

# 3. Compilar o projeto Maven (gera fat JAR com todas as dependências)
cd /workspace
mvn clean package -DskipTests

# 4. Criar os tópicos de input (obrigatório antes de arrancar o Streams)
kafka-topics.sh --create --bootstrap-server broker1:9092 --topic Purchases --partitions 1 --replication-factor 1
kafka-topics.sh --create --bootstrap-server broker1:9092 --topic Sales --partitions 1 --replication-factor 1

# 5. Registar os Kafka Connect connectors (Source + Sink)
cd /workspace/config
./post_connectors.sh

# 6. Correr os 3 componentes (cada um num terminal separado)
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

# Ver eventos a chegar ao Sales
kafka-console-consumer.sh --bootstrap-server broker1:9092 --topic Sales --from-beginning

# Ver resultados Kafka Streams (exemplo: revenue por livro)
kafka-console-consumer.sh --bootstrap-server broker1:9092 --topic Results-revenue-per-book --from-beginning

# Ver dados no PostgreSQL
psql -U postgres -d project3 -c "SELECT * FROM revenue_by_book LIMIT 10;"
psql -U postgres -d project3 -c "SELECT * FROM total_metrics;"
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
python main.py             # REST API     → http://127.0.0.1:8001
python mcp_server.py       # MCP Server   → http://127.0.0.1:8002/sse
python langchain_agent.py  # Agent API    → http://127.0.0.1:8000
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

## Tópicos Kafka

| Tópico | Tipo | Descrição |
|---|---|---|
| `Purchases` | Input | Eventos de compra enviados pelo producer / MCP tool |
| `Sales` | Input | Eventos de venda enviados pelo producer / MCP tool |
| `Results-revenue-per-book` | Output | Revenue por livro (Req #5) |
| `Results-expenses-per-book` | Output | Expenses por livro (Req #6) |
| `Results-profit-per-book` | Output | Profit por livro (Req #7) |
| `Results-total-revenue` | Output | Revenue total (Req #8) |
| `Results-total-expenses` | Output | Expenses total (Req #9) |
| `Results-total-profit` | Output | Profit total (Req #10) |
| `Results-avg-purchase-per-book` | Output | Compra média por livro (Req #11) |
| `Results-avg-purchase-all` | Output | Compra média global (Req #12) |
| `Results-top-profit-book` | Output | Livro com maior lucro (Req #13) |
| `Results-revenue-last-hour` | Output | Revenue última hora (Req #14) |
| `Results-expenses-last-hour` | Output | Expenses última hora (Req #15) |
| `Results-top-country-sales-per-book` | Output | Vendas por país/livro (Req #17) |

> **Nota**: Req #16 (profit última hora) não está implementado no Kafka Streams.

---

## Métricas Calculadas pelo Kafka Streams

| Métrica | Tópico Kafka | Tabela PostgreSQL | Requisito |
|---|---|---|---|
| Revenue por livro | `Results-revenue-per-book` | `revenue_by_book` | #5 |
| Expenses por livro | `Results-expenses-per-book` | `expenses_by_book` | #6 |
| Profit por livro | `Results-profit-per-book` | `profit_by_book` | #7 |
| Total revenue | `Results-total-revenue` | `total_metrics` | #8 |
| Total expenses | `Results-total-expenses` | `total_metrics` | #9 |
| Total profit | `Results-total-profit` | `total_metrics` | #10 |
| Compra média por livro | `Results-avg-purchase-per-book` | `average_purchase_by_book` | #11 |
| Compra média global | `Results-avg-purchase-all` | `total_metrics` | #12 |
| Livro com maior lucro | `Results-top-profit-book` | `total_metrics` | #13 |
| Revenue última hora | `Results-revenue-last-hour` | `time_window_metrics` | #14 |
| Expenses última hora | `Results-expenses-last-hour` | `time_window_metrics` | #15 |
| ~~Profit última hora~~ | ~~`Results-profit-last-hour`~~ | — | ~~#16~~ ❌ |
| Vendas por país/livro | `Results-top-country-sales-per-book` | `best_performing_by_country` | #17 |

---

## Produzir Eventos via Agente IA

O agente LangChain tem acesso a ferramentas MCP que enviam eventos para o Kafka:

- **"Compra 10 exemplares do livro 2 ao fornecedor 1 por 15€"** → `create_purchase_event`
- **"Vende 5 exemplares do livro 3 para Portugal por 20€"** → `create_sale_event`
- **"Gera 10 transações de teste aleatórias"** → `create_test_transactions`

---

## Parar Tudo

```bash
# Parar containers Docker
cd kafka
docker compose -f .devcontainer/docker-compose-standalone.yml down

# Limpar volumes também (reset completo da BD)
docker compose -f .devcontainer/docker-compose-standalone.yml down -v
```

---

## Problemas Conhecidos

- **Req #16 (Profit última hora)** não está implementado no Kafka Streams — requer join entre duas windowed KTables, que o Kafka Streams não suporta diretamente. Workaround: calcular na API como `revenue_last_hour - expenses_last_hour`.
- Os tópicos `Results-*` devem estar **vazios ou com mensagens no formato schema+payload** para os connectors funcionarem. Se houver mensagens antigas em formato plain JSON, apagar os tópicos e reiniciar o Kafka Streams.

Ver `docs/ROADMAP.md` para o estado detalhado dos requisitos.
