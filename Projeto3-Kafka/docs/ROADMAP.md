# Roadmap: MCP + LangChain Agent para Assignment Requirements

## Objetivo
Integrar MCP Server + LangChain Agent para implementar os 17 requisitos da assignment via chat interface.

**Estrutura atual**:
```
Projeto3-Kafka/
├── kafka/    ← Java Kafka Streams (producers, streams, connectors)
├── api/      ← FastAPI + MCP Server + LangChain Agent
├── docs/
└── scripts/
```

---

## 1. MODELS (api/app/models.py)

**Status**: ✅ Completo

- ✅ Author, AuthorCreate, AuthorUpdate
- ✅ Book, BookCreate, BookUpdate (com `cost_price`, `sale_price`) — usado como "Item" da shop
- ✅ Country, CountryCreate, CountryUpdate
- ✅ PurchaseEvent, SaleEvent, ResultEvent (Kafka events)

---

## 2. SERVICES (api/app/services.py)

**Status**: ✅ Completo (exceto Analytics)

### Country CRUD
- ✅ `list_countries()`
- ✅ `get_country()`
- ✅ `create_country()`
- ✅ `update_country()`
- ✅ `delete_country()`

### Book CRUD (usado como Item)
- ✅ `list_books()`, `get_book()`, `create_book()`, `update_book()`, `delete_book()`

### Analytics Query Functions
- ❌ `get_revenue_per_book(session)` — requirement #5
- ❌ `get_expenses_per_book(session)` — requirement #6
- ❌ `get_profit_per_book(session)` — requirement #7
- ❌ `get_total_revenue(session)` — requirement #8
- ❌ `get_total_expenses(session)` — requirement #9
- ❌ `get_total_profit(session)` — requirement #10
- ❌ `get_avg_purchase_per_book(session)` — requirement #11
- ❌ `get_avg_purchase_all(session)` — requirement #12
- ❌ `get_top_profit_book(session)` — requirement #13
- ❌ `get_revenue_last_hour(session)` — requirement #14
- ❌ `get_expenses_last_hour(session)` — requirement #15
- ❌ `get_profit_last_hour(session)` — requirement #16
- ❌ `get_highest_sales_by_country(session, book_id)` — requirement #17

---

## 3. MCP SERVER (api/mcp_server.py)

**Status**: ✅ Parcialmente completo (Analytics em falta)

### Library Tools
- ✅ `list_books_tool()`, `get_book_tool()`, `create_book_tool()`, `update_book_tool()`, `delete_book_tool()`
- ✅ `list_authors_tool()`, `get_author_tool()`, `create_author_tool()`, `update_author_tool()`, `delete_author_tool()`
- ✅ `create_author_from_text_tool()`

### Country Tools (Requirements #1-2)
- ✅ `list_countries_tool()` — requirement #2
- ✅ `get_country_tool(country_id)`
- ✅ `create_country_tool(name, region)` — requirement #1
- ✅ `update_country_tool(country_id, name, region)`
- ✅ `delete_country_tool(country_id)`

### Resources
- ✅ `library://catalog-summary`
- ✅ `library://authors-summary`
- ✅ `library://countries-summary`

### Analytics Tools (FALTA — Requirements #5-17)
- ❌ `get_revenue_per_book_tool()` — requirement #5
- ❌ `get_expenses_per_book_tool()` — requirement #6
- ❌ `get_profit_per_book_tool()` — requirement #7
- ❌ `get_total_revenue_tool()` — requirement #8
- ❌ `get_total_expenses_tool()` — requirement #9
- ❌ `get_total_profit_tool()` — requirement #10
- ❌ `get_avg_purchase_per_book_tool()` — requirement #11
- ❌ `get_avg_purchase_all_tool()` — requirement #12
- ❌ `get_top_profit_book_tool()` — requirement #13
- ❌ `get_revenue_last_hour_tool()` — requirement #14
- ❌ `get_expenses_last_hour_tool()` — requirement #15
- ❌ `get_profit_last_hour_tool()` — requirement #16
- ❌ `get_highest_sales_by_country_tool()` — requirement #17

### Prompt
- ⚠️ `library_assistant_prompt()` — existe mas não inclui contexto de shop/analytics

---

## 4. REST API (api/main.py)

**Status**: ✅ Parcialmente completo (Analytics são placeholders)

### Books
- ✅ `GET /books`, `GET /books/{id}`, `POST /books`, `PATCH /books/{id}`, `DELETE /books/{id}`

### Authors
- ✅ `GET /authors`, `GET /authors/{id}`, `POST /authors`, `PATCH /authors/{id}`, `DELETE /authors/{id}`

### Countries
- ✅ `GET /countries`, `GET /countries/{id}`, `POST /countries`, `PATCH /countries/{id}`, `DELETE /countries/{id}`

### Analytics (placeholders — precisam de dados reais do Kafka)
- ⚠️ `GET /analytics/stats/revenue-per-book` — placeholder
- ⚠️ `GET /analytics/stats/expenses-per-book` — placeholder
- ⚠️ `GET /analytics/stats/profit-per-book` — placeholder
- ⚠️ `GET /analytics/stats/total-revenue` — placeholder
- ⚠️ `GET /analytics/stats/total-expenses` — placeholder
- ⚠️ `GET /analytics/stats/total-profit` — placeholder
- ⚠️ `GET /analytics/stats/average-purchase-per-book` — placeholder
- ⚠️ `GET /analytics/stats/average-purchase-all-books` — placeholder
- ⚠️ `GET /analytics/stats/top-profit-book` — placeholder
- ⚠️ `GET /analytics/stats/revenue-last-hour` — placeholder
- ⚠️ `GET /analytics/stats/expenses-last-hour` — placeholder
- ⚠️ `GET /analytics/stats/profit-last-hour` — placeholder
- ⚠️ `GET /analytics/stats/top-country-sales-per-book` — placeholder

---

## 5. KAFKA STREAMS (kafka/src/)

**Status**: ✅ Compilado e funcional

Métricas implementadas via Kafka Streams e escritas no PostgreSQL:
- ✅ `revenue_by_book` — revenue por livro
- ✅ `expenses_by_book` — expenses por livro
- ✅ `profit_by_book` — profit por livro
- ✅ `total_revenue` — revenue total
- ✅ `total_expenses` — expenses total
- ✅ `total_profit` — profit total
- ✅ `avg_purchase_by_book` — compra média por livro
- ✅ `avg_purchase_all` — compra média global
- ✅ `top_profit_book` — livro com maior lucro
- ✅ `revenue_last_hour` — revenue na última hora (windowed)
- ✅ `expenses_last_hour` — expenses na última hora (windowed)

---

## O Que Falta

### Fase 1: Analytics Services
Implementar em `api/app/services.py` funções que lêem as tabelas do PostgreSQL preenchidas pelo Kafka Streams.

### Fase 2: Analytics MCP Tools
Implementar em `api/mcp_server.py` os 13 tools de analytics (requirements #5-17).

### Fase 3: Conectar REST API ao PostgreSQL real
Substituir os placeholders em `api/main.py` por chamadas reais às funções de services.

### Fase 4: Testar End-to-End
- Kafka Streams a correr → escreve em PostgreSQL
- FastAPI a ler PostgreSQL
- LangChain Agent a chamar MCP tools
- Webapp a funcionar
