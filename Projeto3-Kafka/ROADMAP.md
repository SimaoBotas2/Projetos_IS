# Roadmap: MCP + LangChain Agent para Assignment Requirements

## Objetivo
Integrar MCP Server + LangChain Agent para implementar os 17 requisitos da assignment via chat interface.

---

## 1. VERIFICAR MODELS (app/models.py)

**Status**: ✅ Parcialmente pronto
- ✅ Author, AuthorCreate, AuthorUpdate (Library - KEEP)
- ✅ Book, BookCreate, BookUpdate (com cost_price, sale_price)
- ✅ Country, CountryCreate, CountryUpdate (para requirements #1-2)
- ⚠️ Item, ItemCreate, ItemUpdate (importado mas PRECISA CHECAR se existe)
- ✅ PurchaseEvent, SaleEvent, ResultEvent (Kafka events)

**Ação**:
- [ ] Verificar se Item class existe em models.py (linhas 1-100)
- [ ] Se não existir, pode usar Book como Item (shop context) ou criar Item class separada

---

## 2. COMPLETAR SERVICES (app/services.py)

**Status**: ⚠️ Parcialmente feito

### 2A. Country CRUD (JÁ EXISTE)
- ✅ list_countries() - linha 174
- ✅ get_country() - linha 178
- ✅ create_country() - linha 185
- ❌ update_country() - FALTA
- ❌ delete_country() - FALTA

**Ação**:
- [ ] Adicionar `update_country(session, country_id: int, data: CountryUpdate) -> Country`
  - Similar a update_author (linhas 87-101)
- [ ] Adicionar `delete_country(session, country_id: int) -> dict`
  - Similar a delete_author (linhas 104-114)

### 2B. Item CRUD (FALTA)
**Ação**:
- [ ] Adicionar `list_items(session) -> list[Item]`
  - Copy de list_books (linha 117)
- [ ] Adicionar `get_item(session, item_id: int) -> Item`
  - Copy de get_book (linha 121)
- [ ] Adicionar `create_item(session, data: ItemCreate) -> Item`
  - Similar create_book mas sem author_id (linhas 128-141)
- [ ] Adicionar `update_item(session, item_id: int, data: ItemUpdate) -> Item`
  - Similar update_book (linhas 144-163)
- [ ] Adicionar `delete_item(session, item_id: int) -> dict`
  - Copy de delete_book (linhas 166-170)

### 2C. Analytics Query Functions (FALTA)
**Ação**:
- [ ] Adicionar `get_analytics(session, metric_name: str, key: str = None) -> dict`
  - Query ResultEvent/analytics_results table
  - Parameters: metric_name (ex: "revenue-per-book"), key (ex: book_id)
  - Return: {"metric": name, "key": key, "value": value, "timestamp": ts}

- [ ] Adicionar `get_revenue_per_item(session) -> list[dict]`
  - Query revenue_by_book table
  - Return: [{"book_id": 1, "revenue": 100.50}, ...]

- [ ] Adicionar `get_expenses_per_item(session) -> list[dict]`
  - Query expenses_by_book table

- [ ] Adicionar `get_profit_per_item(session) -> list[dict]`
  - Query profit_by_book table

- [ ] Adicionar `get_total_metrics(session) -> dict`
  - Query total_metrics table
  - Return: {"total_revenue": X, "total_expenses": Y, "total_profit": Z}

- [ ] Adicionar `get_top_profit_item(session) -> dict`
  - Query profit_by_book ORDER BY DESC LIMIT 1
  - Return: {"book_id": X, "profit": Y}

- [ ] Adicionar `get_time_window_metrics(session, metric_type: str) -> list[dict]`
  - Query time_window_metrics
  - Return: [{"window_start": ts, "metric_value": X}, ...]

- [ ] Adicionar `get_sales_by_country(session, book_id: int) -> list[dict]`
  - Query best_performing_by_country
  - Return: [{"country_id": 1, "revenue": X, "sales_volume": Y}, ...]

---

## 3. ESTENDER MCP SERVER (mcp_server.py)

**Status**: ❌ Precisa estender

### 3A. Imports (linha 8-23)
**Ação**:
- [ ] Adicionar imports de Country functions:
  ```python
  from app.services import (
      ...existing imports...,
      CountryNotFoundError, CountryCreate, CountryUpdate,
      create_country, get_country, list_countries, update_country, delete_country,
      ItemNotFoundError, ItemCreate, ItemUpdate,
      list_items, get_item, create_item, update_item, delete_item,
  )
  ```

- [ ] Adicionar imports de Country models:
  ```python
  from app.models import CountryCreate, CountryUpdate, ItemCreate, ItemUpdate
  ```

### 3B. Country Tools (depois da linha 100)
**Ação**:
- [ ] Adicionar `list_countries_tool()` - lista todos os países
- [ ] Adicionar `get_country_tool(country_id: int)` - get país específico
- [ ] Adicionar `create_country_tool(name: str, region: str)` - add país
- [ ] Adicionar `update_country_tool(country_id: int, name: str = None, region: str = None)` - update
- [ ] Adicionar `delete_country_tool(country_id: int)` - remove país

### 3C. Item Tools
**Ação**:
- [ ] Adicionar `list_items_tool()` - lista todos items
- [ ] Adicionar `get_item_tool(item_id: int)` - get item
- [ ] Adicionar `create_item_tool(title: str, cost_price: float, sale_price: float)` - add item
- [ ] Adicionar `update_item_tool(item_id: int, ...)` - update item
- [ ] Adicionar `delete_item_tool(item_id: int)` - remove item

### 3D. Analytics Tools (para os 17 requisitos)
**Ação**:
- [ ] `get_revenue_per_item_tool()` - requirement #5
- [ ] `get_expenses_per_item_tool()` - requirement #6
- [ ] `get_profit_per_item_tool()` - requirement #7
- [ ] `get_total_revenue_tool()` - requirement #8
- [ ] `get_total_expenses_tool()` - requirement #9
- [ ] `get_total_profit_tool()` - requirement #10
- [ ] `get_avg_purchase_per_item_tool()` - requirement #11
- [ ] `get_avg_purchase_all_tool()` - requirement #12
- [ ] `get_top_profit_item_tool()` - requirement #13
- [ ] `get_revenue_last_hour_tool()` - requirement #14
- [ ] `get_expenses_last_hour_tool()` - requirement #15
- [ ] `get_profit_last_hour_tool()` - requirement #16
- [ ] `get_highest_sales_by_country_tool()` - requirement #17

### 3E. Prompt (linha 48-57)
**Ação**:
- [ ] Estender `library_assistant_prompt()` para incluir shop operations
  - Ou criar `shop_assistant_prompt()` novo

---

## 4. ATUALIZAR REST API (main.py)

**Status**: ❓ Desconhecido

**Ação**:
- [ ] Verificar se existem endpoints para /countries
- [ ] Adicionar se não existir:
  - GET /countries
  - GET /countries/{id}
  - POST /countries (create)
  - PUT /countries/{id} (update)
  - DELETE /countries/{id} (delete)

- [ ] Verificar se existem endpoints para /items
  - GET /items
  - GET /items/{id}
  - POST /items
  - PUT /items/{id}
  - DELETE /items/{id}

- [ ] Adicionar endpoint para analytics:
  - GET /analytics?metric=<name>&key=<key>

---

## 5. TESTAR INTEGRAÇÃO

**Ação**:
- [ ] Rodar MCP Server
- [ ] Verificar se todos os tools aparecem
- [ ] Testar LangChain Agent com queries como:
  - "Add country France in Europe"
  - "List all countries"
  - "What's the revenue per item?"
  - "Show me the top profit item"
  - "Which country has highest sales for book 1?"

---

## 6. ATUALIZAR FRONTEND (se necessário)

**Status**: ❓ Verificar webapp.html

**Ação**:
- [ ] Testar se webapp consegue comunicar com agent
- [ ] Adicionar instrução no prompt do agent sobre shop context

---

## Checklist de Implementação

### Phase 1: Services
- [ ] update_country + delete_country
- [ ] Item CRUD functions (5 funções)
- [ ] Analytics query functions (8+ funções)
- **Total**: ~25 linhas novas

### Phase 2: MCP Server
- [ ] Country imports + tools (5 tools)
- [ ] Item imports + tools (5 tools)
- [ ] Analytics tools (13 tools)
- [ ] Update prompt
- **Total**: ~150-200 linhas novas

### Phase 3: REST API
- [ ] Country endpoints (5)
- [ ] Item endpoints (5)
- [ ] Analytics endpoint (1)
- **Total**: ~30 linhas novas

### Phase 4: Testing
- [ ] MCP tools working
- [ ] Agent calls tools correctly
- [ ] Frontend integration
- [ ] End-to-end workflow

---

## Estimativa de Tempo
- Services: 20 min
- MCP Server: 40 min
- REST API: 15 min
- Testing: 20 min
- **Total**: ~95 min

---

## Arquivos a Modificar
1. `ProjetoBase_MCP_Agent_Web/app/services.py` - +30 linhas
2. `ProjetoBase_MCP_Agent_Web/mcp_server.py` - +200 linhas
3. `ProjetoBase_MCP_Agent_Web/main.py` - +30 linhas
4. `ProjetoBase_MCP_Agent_Web/app/models.py` - verify Item exists

**Sem modificar**:
- app/models.py (deve estar ok)
- langchain_agent.py (reutilizar)
- webapp.html (deve funcionar)

---

## Próximo Passo
Implementar **Phase 1: Services** seguindo este roadmap.
