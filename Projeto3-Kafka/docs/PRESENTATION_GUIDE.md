# Guia de Apresentação — Projeto 3 Kafka

## SLIDE 1 — Título

**Título**: Projeto 3 — Message-Oriented Middleware com Apache Kafka  
**Subtítulo**: Processamento de eventos em tempo real com Kafka Streams, Kafka Connect e Agente IA  
**Footer**: Integração de Sistemas — MEI 2025/26 | [Nomes do grupo]

---

## SLIDE 2 — Arquitetura Geral

Desenhar fluxo da esquerda para a direita:

```
[Produtores de Eventos]          [Agente IA / MCP]
   PurchaseEventProducer    +    LangChain Agent
   SaleEventProducer              ↓
          ↓                  create_sale_event / create_purchase_event
          ↓_______________________________↓
                    [Apache Kafka]
              Tópicos: Purchases | Sales
                           ↓
              [Kafka Streams — Java]
              ProjetoBase3Streams.java
              (aggregate, join, reduce, window)
                           ↓
              [13 Tópicos Results-*]
                           ↓
           [Kafka Connect — 13 JDBC Sinks]
                           ↓
                    [PostgreSQL]
                    6 tabelas analíticas
                           ↑
               [FastAPI REST API :8001]
                           ↑
           [MCP Server :8002 + LangChain Agent :8000]
                           ↑
                      [Webapp HTML]
```

Também mostrar Kafka Connect Source: `PostgreSQL → DBInfo topic` (lê books/countries da BD para Kafka).

**Ponto-chave**: O fluxo é totalmente event-driven. Nenhum componente faz queries à BD para calcular métricas — tudo é processado em Kafka Streams.

---

## SLIDE 3 — Stack Tecnológico

**Lado Kafka (Java/Docker)**
- Apache Kafka 3.x (KRaft mode, sem Zookeeper)
- Kafka Streams API — processamento stateful em tempo real
- Kafka Connect — JDBC Source + 13 JDBC Sinks (Confluent)
- PostgreSQL 15 — persistência das métricas
- Docker Compose — orquestração de todos os serviços

**Lado API (Python)**
- FastAPI — REST API (endpoints CRUD + analytics)
- MCP (Model Context Protocol) — server com tools para agente
- LangChain + OpenAI — agente em linguagem natural
- SQLModel + psycopg2 — acesso ao PostgreSQL

---

## SLIDE 4 — Tópicos Kafka e Tabelas PostgreSQL

| Tópico Kafka | Tabela PostgreSQL | Requisito |
|---|---|---|
| Purchases, Sales | (input) | — |
| Results-revenue-per-book | revenue_by_book | #5 |
| Results-expenses-per-book | expenses_by_book | #6 |
| Results-profit-per-book | profit_by_book | #7 |
| Results-total-revenue | total_metrics | #8 |
| Results-total-expenses | total_metrics | #9 |
| Results-total-profit | total_metrics | #10 |
| Results-avg-purchase-per-book | average_purchase_by_book | #11 |
| Results-avg-purchase-all | total_metrics | #12 |
| Results-top-profit-book | total_metrics | #13 |
| Results-revenue-last-hour | time_window_metrics | #14 |
| Results-expenses-last-hour | time_window_metrics | #15 |
| Results-profit-last-hour | time_window_metrics | #16 |
| Results-top-country-sales-per-book | best_performing_by_country | #17 |

**Ponto-chave**: Formato das mensagens nos tópicos Results = JSON com schema embutido — envelope `{"schema":{...}, "payload":{...}}` exigido pelo Kafka Connect JsonConverter sem Schema Registry.

---

## SLIDE 5 — Kafka Streams: Operações Utilizadas

- **`aggregate()`** — acumula revenue/expenses por book_id à medida que chegam eventos. Usado em Req #5, #6, #8, #9, #17
- **`join()` KTable-KTable** — combina duas KTables para calcular profit = revenue − expenses. Usado em Req #7, #10, #12
- **`reduce()`** — mantém o máximo corrente (livro com maior lucro). Usado em Req #13
- **`windowedBy(TimeWindows.of(Duration.ofHours(1)))`** — janela temporal de 1 hora, recalculada a cada novo evento. Usado em Req #14, #15, #16
- **Chave composta** — agrupa por `"bookId_countryId"` para encontrar o país com mais vendas por livro. Usado em Req #17

---

## SLIDE 6 — Kafka Connect: O Desafio Técnico Resolvido

**Problema encontrado**: O JDBC Sink Connector exige que as mensagens Kafka tenham um schema associado para conseguir mapear os campos ao schema da tabela PostgreSQL.

**Tentativas falhadas**:
- `pk.mode=kafka` → erro "requires non-null Struct schema"
- `schemas.enable=false` → JsonConverter rejeita sem schema

**Solução implementada**: O próprio Kafka Streams produz JSON com schema embutido:

```json
{
  "schema": {
    "type": "struct",
    "fields": [
      {"type": "int32", "field": "book_id"},
      {"type": "double", "field": "revenue"}
    ]
  },
  "payload": {
    "book_id": 1,
    "revenue": 45.00
  }
}
```

Sem Schema Registry, sem Avro — schema inline, 13 sinks funcionam com `pk.mode=record_value`.

**Este é um ponto forte na apresentação** — demonstra resolução de problemas reais para além do setup tutorial.

---

## SLIDE 7 — REST API (FastAPI)

**Endpoints CRUD**:
- `GET/POST /books` — listar e criar livros (Req #3, #4)
- `GET/POST /countries` — listar e criar países (Req #1, #2)
- `GET/POST /authors` — gestão de autores

**Endpoints Analytics** (13 endpoints):
- `/analytics/stats/revenue-per-book`
- `/analytics/stats/total-revenue`
- `/analytics/stats/avg-purchase-per-book`
- `/analytics/stats/revenue-last-hour`
- `/analytics/stats/profit-last-hour`
- `/analytics/stats/top-country-sales-per-book`
- `/analytics/stats/dashboard` — todos os dados de uma vez

---

## SLIDE 8 — MCP Server + LangChain Agent

**MCP (Model Context Protocol)**: Framework que expõe funções Python como "tools" que um LLM pode invocar.

**Como funciona**:
1. Utilizador escreve em linguagem natural na webapp
2. LangChain Agent analisa a intenção
3. Seleciona a tool MCP adequada
4. Executa a função Python real
5. Devolve resultado formatado

**Exemplos de tools**:

| Pergunta do utilizador | Tool MCP invocada |
|---|---|
| "Qual é o revenue total?" | `get_total_revenue_tool` |
| "Gera 10 transações de teste" | `create_test_transactions` |
| "Qual país tem mais vendas do livro 2?" | `get_top_country_sales_per_book_tool` |
| "Adiciona o país Itália, região Europa" | `create_country_tool` |
| "Qual o livro com maior lucro?" | `get_top_profit_book_tool` |

---

## SLIDE 9 — Demonstração ao Vivo

Sequência sugerida:
1. Abrir webapp (`api/webapp.html`) — mostrar interface de chat
2. Pedir ao agente para gerar transações: *"Generate 10 test transactions"*
3. Mostrar Kafka a receber mensagens num terminal
4. Mostrar PostgreSQL com os dados a aparecer nas tabelas
5. Consultar analytics: *"What is the total revenue?"*, *"Which book has the highest profit?"*
6. CRUD: *"Add country Italy, region Europe"* → confirmar com *"List all countries"*

---

## SLIDE 10 — Requisitos: Estado Final

| Req | Descrição | Estado |
|---|---|---|
| #1 | Add country | ✅ |
| #2 | List countries | ✅ |
| #3 | Add item (book) | ✅ |
| #4 | List items (books) | ✅ |
| #5 | Revenue per book | ✅ |
| #6 | Expenses per book | ✅ |
| #7 | Profit per book | ✅ |
| #8 | Total revenue | ✅ |
| #9 | Total expenses | ✅ |
| #10 | Total profit | ✅ |
| #11 | Avg purchase per book | ✅ |
| #12 | Avg purchase all | ✅ |
| #13 | Top profit book | ✅ |
| #14 | Revenue last hour | ✅ |
| #15 | Expenses last hour | ✅ |
| #16 | Profit last hour | ✅ |
| #17 | Top country per book | ✅ |

**17 de 17 requisitos implementados.**

---

## SLIDE 11 — Conclusões

**O que foi conseguido**:
- Pipeline Kafka end-to-end completamente funcional
- Todos os 17 requisitos implementados
- Processamento em tempo real sem queries diretas à BD para métricas
- Kafka Connect automatiza persistência (apenas configuração JSON, zero código de escrita à BD)
- Interface em linguagem natural via MCP + LangChain

**Aprendizagens técnicas**:
- Kafka Streams: processamento stateful com KTables, joins e janelas temporais
- Kafka Connect: integração declarativa entre sistemas heterogéneos
- O desafio do schema JSON — diferença entre `schemas.enable=true/false` e Schema Registry
- MCP Protocol: forma elegante de expor lógica de negócio a agentes IA

**Possíveis extensões**:
- Dashboard web em tempo real com WebSockets
- Alertas automáticos quando profit desce abaixo de threshold
- Escalar para múltiplos brokers Kafka (já preparado com KRaft)
