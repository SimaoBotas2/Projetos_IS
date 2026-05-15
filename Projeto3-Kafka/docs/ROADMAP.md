# Roadmap: Projeto 3 — Estado Atual e Bugs

## Estado Geral

| Componente | Estado |
|---|---|
| Kafka Streams topology (13 métricas) | ✅ Implementado — ⚠️ Não produz output (ver bugs) |
| REST API (CRUD + Analytics) | ✅ Implementado — ⚠️ Analytics com nomes de tabelas errados |
| MCP Server (todas as tools) | ✅ Implementado |
| LangChain Agent | ✅ Funcional |
| Kafka Connect Sink connectors | ⚠️ Apenas 4 de 13 configurados |
| Base de dados persistente | ✅ Volume Docker configurado |
| MCP Kafka Producer tools | ✅ Implementado |

---

## 🐛 Bugs Conhecidos (por ordem de prioridade)

### BUG 1 — CRÍTICO: Schema da BD incompatível com services.py

`services.py` consulta tabelas com nomes diferentes dos que existem na BD:

| services.py consulta | Tabela real na BD | Fix necessário |
|---|---|---|
| `total_revenue` | `total_metrics` (coluna `metric_value`) | Corrigir query em services.py |
| `total_expenses` | `total_metrics` | Corrigir query |
| `total_profit` | `total_metrics` | Corrigir query |
| `average_purchase` | não existe | Corrigir para `total_metrics` |
| `avg_purchase_by_book` | `average_purchase_by_book` | Corrigir nome da tabela |
| `top_profit_book` | não existe | Corrigir para `total_metrics` |
| `revenue_last_hour` | `time_window_metrics` | Corrigir query |
| `expenses_last_hour` | `time_window_metrics` | Corrigir query |
| `profit_last_hour` | `time_window_metrics` | Corrigir query |
| `top_sales_by_country_per_book` | `best_performing_by_country` | Corrigir nome |

### BUG 2 — CRÍTICO: Tabela `books` na BD não tem colunas `author` e `author_id`

O ficheiro `kafka/sql/create_tables.sql` é executado pelo Docker ao arrancar e cria a tabela `books` **sem** as colunas `author` e `author_id`. O SQLModel não recria tabelas que já existem.

**Resultado**: `POST /books` falha com erro de coluna inexistente.

**Fix**: Atualizar `kafka/sql/create_tables.sql` para incluir tabela `author` e colunas FK na tabela `books`.

### BUG 3 — CRÍTICO: Kafka Streams não produz output para tópicos Results-*

O Kafka Streams consome corretamente do tópico `Sales` (LAG=0 verificado) mas não escreve nos tópicos `Results-*`. Causa provável:

- Erro de serialização no `MetricEventSerde`
- Exceção silenciosa na topology (verificar logs do `java -jar`)
- `streams.cleanUp()` chamado no startup pode causar problemas de estado

**Fix**: Examinar logs da aplicação Java ao arrancar. Procurar por `ERROR` ou `Exception`.

### BUG 4 — ALTO: Kafka Connect Sink connectors em falta

Existem apenas **4 conectores** configurados para **13 tópicos** de resultado:

| Conector | Estado |
|---|---|
| `sink-revenue-per-book` | ✅ Existe |
| `sink-expenses-per-book` | ✅ Existe |
| `sink-profit-per-book` | ✅ Existe |
| `sink-total-revenue` | ✅ Existe |
| `sink-total-expenses` | ❌ Falta |
| `sink-total-profit` | ❌ Falta |
| `sink-avg-purchase-per-book` | ❌ Falta |
| `sink-avg-purchase-all` | ❌ Falta |
| `sink-top-profit-book` | ❌ Falta |
| `sink-revenue-last-hour` | ❌ Falta |
| `sink-expenses-last-hour` | ❌ Falta |
| `sink-profit-last-hour` | ❌ Falta |
| `sink-top-country-sales` | ❌ Falta |

### BUG 5 — MÉDIO: Kafka Streams usa `broker2` que não existe

`ProjetoBase3Streams.java` linha 19:
```java
properties.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "broker1:9092,broker2:9092");
```
Apenas `broker1` existe no docker-compose. Deve ser apenas `"broker1:9092"`.

### BUG 6 — MÉDIO: `Results-total-expenses` usa Serde errado

`ProjetoBase3Streams.java` linha 117 usa `Serdes.Double()` em vez de `metricSerde`:
```java
.to("Results-total-expenses", Produced.with(Serdes.String(), Serdes.Double()));
```
Inconsistente com todos os outros tópicos que usam `MetricEvent`.

### BUG 7 — BAIXO: Req #16 (Profit última hora) não implementado

O código Kafka Streams tem um comentário `// would require joining windowed tables` mas não implementa o cálculo. O tópico `Results-profit-last-hour` nunca recebe dados.

---

## Estado por Requisito do Assignment

| Req | Descrição | API | MCP Tool | Kafka Streams | Sink Connector | BD |
|---|---|---|---|---|---|---|
| #1 | Add country | ✅ | ✅ | — | — | ✅ |
| #2 | List countries | ✅ | ✅ | — | — | ✅ |
| #3 | Add item (book) | ⚠️ Bug #2 | ⚠️ Bug #2 | — | — | ⚠️ |
| #4 | List items (books) | ✅ | ✅ | — | — | ✅ |
| #5 | Revenue per book | ⚠️ Bug #1 | ⚠️ Bug #1 | ⚠️ Bug #3 | ✅ | ✅ |
| #6 | Expenses per book | ⚠️ Bug #1 | ⚠️ Bug #1 | ⚠️ Bug #3 | ✅ | ✅ |
| #7 | Profit per book | ⚠️ Bug #1 | ⚠️ Bug #1 | ⚠️ Bug #3 | ✅ | ✅ |
| #8 | Total revenue | ⚠️ Bug #1 | ⚠️ Bug #1 | ⚠️ Bug #3 | ✅ | ✅ |
| #9 | Total expenses | ⚠️ Bug #1 | ⚠️ Bug #1 | ⚠️ Bug #3 | ❌ Bug #4 | ✅ |
| #10 | Total profit | ⚠️ Bug #1 | ⚠️ Bug #1 | ⚠️ Bug #3 | ❌ Bug #4 | ✅ |
| #11 | Avg purchase/book | ⚠️ Bug #1 | ⚠️ Bug #1 | ⚠️ Bug #3 | ❌ Bug #4 | ✅ |
| #12 | Avg purchase all | ⚠️ Bug #1 | ⚠️ Bug #1 | ⚠️ Bug #3 | ❌ Bug #4 | ✅ |
| #13 | Top profit book | ⚠️ Bug #1 | ⚠️ Bug #1 | ⚠️ Bug #3 | ❌ Bug #4 | ✅ |
| #14 | Revenue last hour | ⚠️ Bug #1 | ⚠️ Bug #1 | ⚠️ Bug #3 | ❌ Bug #4 | ✅ |
| #15 | Expenses last hour | ⚠️ Bug #1 | ⚠️ Bug #1 | ⚠️ Bug #3 | ❌ Bug #4 | ✅ |
| #16 | Profit last hour | ⚠️ Bug #1 | ⚠️ Bug #1 | ❌ Bug #7 | ❌ | ✅ |
| #17 | Top country/book | ⚠️ Bug #1 | ⚠️ Bug #1 | ⚠️ Bug #3 | ❌ Bug #4 | ✅ |

---

## O Que Está Implementado (mas precisa de fix)

### Models (api/app/models.py) ✅
- Author, AuthorCreate, AuthorUpdate
- Book, BookCreate, BookUpdate (com `cost_price`, `sale_price`, `author_id`)
- Country, CountryCreate, CountryUpdate
- PurchaseEvent, SaleEvent, ResultEvent

### Services (api/app/services.py) ✅ (implementado, ⚠️ nomes de tabelas errados)
- Author CRUD completo
- Book CRUD completo
- Country CRUD completo
- Todas as 13 funções de analytics (queries com nomes de tabelas incorretos — Bug #1)

### REST API (api/main.py) ✅
- CRUD: `/authors`, `/books`, `/countries`
- Analytics: `/analytics/stats/*` (13 endpoints)
- Dashboard: `/analytics/stats/dashboard`

### MCP Server (api/mcp_server.py) ✅
- Tools CRUD para Author, Book, Country
- 13 tools de analytics (Req #5–17)
- Tools Kafka: `create_purchase_event`, `create_sale_event`, `create_test_transactions`
- Resources: `library://catalog-summary`, `library://authors-summary`, `library://countries-summary`

### Kafka Streams (kafka/src/) ✅ topology, ⚠️ não produz output
- 13 métricas definidas na topology
- MetricEvent POJO + Serde
- Windowed aggregations para última hora

### Base de Dados ✅
- Persistência via Docker volume (`postgres_data`)
- Tabelas de analytics criadas pelo init SQL
- Tabelas CRUD geridas pelo SQLModel

---

## Plano de Fix (por ordem)

1. **Fix Bug #2**: Atualizar `kafka/sql/create_tables.sql` — adicionar `authors` table e colunas FK em `books`
2. **Fix Bug #3**: Examinar logs Kafka Streams, identificar e corrigir erro de serialização
3. **Fix Bug #5**: Remover `broker2` do bootstrap servers em `ProjetoBase3Streams.java`
4. **Fix Bug #6**: Mudar `Serdes.Double()` para `metricSerde` na linha 117
5. **Fix Bug #4**: Criar 9 sink connectors em falta em `kafka/config/`
6. **Fix Bug #1**: Corrigir queries em `services.py` para usar nomes reais das tabelas
7. **Fix Bug #7**: Implementar profit-last-hour no Kafka Streams (join de windowed tables)
