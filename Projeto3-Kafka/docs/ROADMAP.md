# Roadmap: Projeto 3 — Estado Atual

## Estado Geral

| Componente | Estado |
|---|---|
| Kafka Streams topology (12 métricas) | ✅ Funcional — produz schema+payload JSON |
| REST API (CRUD + Analytics) | ✅ Implementado e funcional |
| MCP Server (todas as tools) | ✅ Implementado |
| LangChain Agent | ✅ Funcional |
| Kafka Connect (13 connectors) | ✅ Todos registados e a escrever na BD |
| Base de dados PostgreSQL | ✅ Dados a chegar em tempo real |
| MCP Kafka Producer tools | ✅ Implementado |

---

## Bugs Resolvidos

| Bug | Severidade | Descrição | Estado |
|---|---|---|---|
| #1 | CRÍTICO | `services.py` consultava tabelas com nomes errados | ✅ Corrigido |
| #2 | CRÍTICO | Tabela `book` sem colunas `author` e `author_id` | ✅ Corrigido em `create_tables.sql` |
| #3 | CRÍTICO | Kafka Streams não produzia output | ✅ Corrigido — usa schema+payload JSON |
| #4 | ALTO | Apenas 4 de 13 sink connectors configurados | ✅ Corrigido — todos os 13 existem |
| #5 | MÉDIO | Kafka Streams referenciava `broker2` inexistente | ✅ Corrigido — só `broker1:9092` |
| #6 | MÉDIO | `Results-total-expenses` usava Serde errado | ✅ Corrigido — usa `totalMetricJson()` |

---

## Problema Conhecido / Não Implementado

### Req #16 — Profit Última Hora

O `Results-profit-last-hour` não está implementado. Requereria um join entre duas KTables com janela temporal (`windowedBy`), o que em Kafka Streams não é suportado diretamente da forma mais simples.

**Workaround possível**: calcular `profit_last_hour = revenue_last_hour - expenses_last_hour` no lado da API ao ler de `time_window_metrics`.

---

## Estado por Requisito do Assignment

| Req | Descrição | API | MCP Tool | Kafka Streams | Sink Connector | BD |
|---|---|---|---|---|---|---|
| #1 | Add country | ✅ | ✅ | — | — | ✅ |
| #2 | List countries | ✅ | ✅ | — | — | ✅ |
| #3 | Add item (book) | ✅ | ✅ | — | — | ✅ |
| #4 | List items (books) | ✅ | ✅ | — | — | ✅ |
| #5 | Revenue per book | ✅ | ✅ | ✅ | ✅ | ✅ |
| #6 | Expenses per book | ✅ | ✅ | ✅ | ✅ | ✅ |
| #7 | Profit per book | ✅ | ✅ | ✅ | ✅ | ✅ |
| #8 | Total revenue | ✅ | ✅ | ✅ | ✅ | ✅ |
| #9 | Total expenses | ✅ | ✅ | ✅ | ✅ | ✅ |
| #10 | Total profit | ✅ | ✅ | ✅ | ✅ | ✅ |
| #11 | Avg purchase/book | ✅ | ✅ | ✅ | ✅ | ✅ |
| #12 | Avg purchase all | ✅ | ✅ | ✅ | ✅ | ✅ |
| #13 | Top profit book | ✅ | ✅ | ✅ | ✅ | ✅ |
| #14 | Revenue last hour | ✅ | ✅ | ✅ | ✅ | ✅ |
| #15 | Expenses last hour | ✅ | ✅ | ✅ | ✅ | ✅ |
| #16 | Profit last hour | ⚠️ | ⚠️ | ❌ | ❌ | — |
| #17 | Top country/book | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## O Que Está Implementado

### Models (`api/app/models.py`) ✅
- Author, AuthorCreate, AuthorUpdate
- Book, BookCreate, BookUpdate (com `cost_price`, `sale_price`, `author_id`)
- Country, CountryCreate, CountryUpdate
- PurchaseEvent, SaleEvent, ResultEvent

### Services (`api/app/services.py`) ✅
- Author CRUD completo
- Book CRUD completo
- Country CRUD completo
- Todas as 13 funções de analytics com queries corretas

### REST API (`api/main.py`) ✅
- CRUD: `/authors`, `/books`, `/countries`
- Analytics: `/analytics/stats/*` (13 endpoints)
- Dashboard: `/analytics/stats/dashboard`

### MCP Server (`api/mcp_server.py`) ✅
- Tools CRUD para Author, Book, Country
- 13 tools de analytics (Req #5–17)
- Tools Kafka: `create_purchase_event`, `create_sale_event`, `create_test_transactions`

### Kafka Streams (`kafka/src/`) ✅
- 12 métricas implementadas e a produzir para PostgreSQL
- Schema+payload JSON embutido (sem Schema Registry)
- `LogAndContinueExceptionHandler` — mensagens malformadas são ignoradas
- `PurchaseEvent.fromJson()` — `supplier_id` é opcional
