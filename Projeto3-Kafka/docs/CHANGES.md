# Mudanças - Conectar MCP_AGENT ao PostgreSQL do Kafka

**Data**: 2026-05-12  
**Objetivo**: Conectar MCP_AGENT ao PostgreSQL do Kafka em vez de SQLite local

---

## Fase 1: Configurar Banco de Dados

### ✅ Passo 1.1: Adicionar psycopg2 a requirements.txt
**Arquivo**: `requirements.txt`  
**Mudança**: Adicionar driver PostgreSQL  
**Status**: ✅ FEITO

```diff
+ psycopg2-binary==2.9.9
```

### ✅ Passo 1.2: Atualizar db.py para PostgreSQL
**Arquivo**: `app/db.py`  
**Mudança 1**: Trocar SQLite por PostgreSQL Docker  
**Status**: ✅ FEITO

```diff
- DATABASE_URL = "sqlite:///library.db"
+ DATABASE_URL = "postgresql://postgres:nopass@localhost:5432/project3"
```

**Mudança 2**: Remover função SQLite-específica (_migrate_book_table)  
**Por quê**: PRAGMA não funciona em PostgreSQL, schema é gerenciado por Kafka Connect  
**Status**: ✅ FEITO

**Resultado final de db.py**:
```python
from sqlmodel import Session, SQLModel, create_engine

# PostgreSQL connection to Kafka project database
DATABASE_URL = "postgresql://postgres:nopass@localhost:5432/project3"
engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables() -> None:
    """Create tables. PostgreSQL schema is managed by Kafka Connect."""
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

**Status**: ✅ FASE 1 COMPLETA

---

## Fase 2: Verificar Models

### ✅ Passo 2.1: Verificar modelos em models.py
**Status**: ✅ FEITO - DESCOBERTA: Country JÁ EXISTE!

**Modelos presentes**:
- ✅ Author, AuthorCreate, AuthorUpdate (Library)
- ✅ Book, BookCreate, BookUpdate (Intacto, sem mudanças)
- ✅ Country, CountryCreate, CountryUpdate (Para requisitos #1-2)
- ✅ PurchaseEvent, SaleEvent, ResultEvent (Kafka events)

---

## Fase 3: Estender Services (app/services.py)

### ✅ Passo 3.1: Remover imports de Item
**Arquivo**: `app/services.py` linhas 5-10  
**Por quê**: Item não existe em models.py  
**Status**: ✅ FEITO

```diff
- Item, ItemCreate, ItemUpdate
```

### ✅ Passo 3.2: Remover exception ItemNotFoundError
**Por quê**: Não é mais usada  
**Status**: ✅ FEITO

### ✅ Passo 3.3: Adicionar update_country()
**Arquivo**: `app/services.py` após create_country()  
**Função**: Atualiza um país existente  
**Status**: ✅ FEITO

```python
def update_country(session: Session, country_id: int, data: CountryUpdate) -> Country:
    country = get_country(session, country_id)
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(country, key, value)
    session.add(country)
    session.commit()
    session.refresh(country)
    return country
```

### ✅ Passo 3.4: Adicionar delete_country()
**Arquivo**: `app/services.py` após update_country()  
**Função**: Delete um país e retorna status  
**Status**: ✅ FEITO

```python
def delete_country(session: Session, country_id: int) -> dict:
    country = get_country(session, country_id)
    session.delete(country)
    session.commit()
    return {"status": "deleted", "id": country_id}
```

### ✅ Status da Fase 3: COMPLETA

**Funções Country agora disponíveis**:
- ✅ list_countries() - listar todos
- ✅ get_country() - get por ID
- ✅ create_country() - criar novo
- ✅ update_country() - atualizar
- ✅ delete_country() - deletar

---

## Fase 4: Estender MCP Server (mcp_server.py)

### ✅ Passo 4.1: Adicionar imports de Country
**Arquivo**: `mcp_server.py` linhas 7-23  
**O que adicionar**: 
- Modelos: CountryCreate, CountryUpdate
- Exceção: CountryNotFoundError
- Funções: create_country, get_country, list_countries, update_country, delete_country

**Status**: ✅ FEITO

### ✅ Passo 4.2: Adicionar 5 Country Tools
**Arquivo**: `mcp_server.py` antes do `if __name__ == "__main__"`  
**Tools adicionadas**:

1. **list_countries_tool()** - Requirement #2
   - Lista todos os países
   - Return: list[dict]

2. **get_country_tool(country_id: int)** - Detalhe de um país
   - Get país por ID
   - Return: dict

3. **create_country_tool(name: str, region: str)** - Requirement #1
   - Cria novo país
   - Return: dict (país criado)

4. **update_country_tool(country_id: int, name: str | None, region: str | None)**
   - Atualiza país existente
   - Return: dict (país atualizado)

5. **delete_country_tool(country_id: int)**
   - Deleta um país
   - Return: dict {"status": "deleted", "id": country_id}

**Status**: ✅ FEITO

### ✅ Passo 4.3: Adicionar Resource para Resumo
**Arquivo**: `mcp_server.py`  
**Resource**: `countries_summary()`
- Retorna plain-text com lista formatada de países
- Padrão: `{id}: {name} ({region})`

**Status**: ✅ FEITO

### ✅ Status da Fase 4: COMPLETA

---

## Checklist Final

- [x] db.py conectado ao PostgreSQL
- [x] Models verificados (Country já existe)
- [x] Services expandido (Country CRUD completo)
- [x] MCP Server com Country tools (5 tools + 1 resource)
- [x] Teste de conexão com banco
- [x] LangChain Agent funcional com tools MCP
- [x] Webapp funcional

## Fases Completadas Posteriormente

- [x] Analytics Models em models.py
- [x] Analytics Query Functions em services.py (13 funções, queries corretas)
- [x] Analytics Tools em mcp_server.py (13+ tools)
- [x] Pipeline Kafka Streams → Kafka Connect → PostgreSQL a funcionar
- [x] Schema+payload JSON fix (ver SESSION_STATE.md)

