# Preparação para a Defesa Oral — Projeto #3 Kafka

---

## ⚠️ Nota crítica — O que o professor avalia

Um colega fez o projeto em Python **sem Kafka Streams** e o professor **recusou avaliar** — disse que sem Streams não havia trabalho.  
O Kafka Streams é o núcleo do projeto. Deves conseguir explicar:
1. O que o Streams faz e porquê é necessário
2. Como usaste `aggregate`, `reduce`, `groupBy`, `join`, `windowedBy` — com exemplos reais do teu código
3. ISR, Replication Factor — o que significam e o que acontece quando algo falha
4. Cenários de falha concretos: "se um producer cai, continua a dar p ler? dá p escrever?"

---

## 1. Conceitos Base do Kafka

### O que é o Kafka?
Uma plataforma distribuída de streaming de eventos. Os producers escrevem mensagens para tópicos, os consumers lêem a partir deles. O Kafka guarda as mensagens de forma durável e permite reproduzi-las.

### Producer
Envia mensagens para um tópico Kafka. Neste projeto: `PurchaseEventProducer`, `SaleEventProducer`, e o MCP tool `create_test_transactions`.

### Consumer
Lê mensagens de um tópico. O Kafka regista quais as mensagens que cada consumer já leu através de **offsets**. Um consumer pode ler desde o início (`--from-beginning`) ou apenas novas mensagens.

### Consumer Groups
Vários consumers no mesmo grupo partilham o trabalho — cada partição é atribuída a apenas um consumer do grupo. Isto permite escalamento horizontal. O Kafka Streams usa consumer groups internamente.

### Tópico
Um fluxo de mensagens com nome. As mensagens estão ordenadas dentro de uma partição, mas não entre partições. Neste projeto: `Sales`, `Purchases`, `DBInfo`, e 13 tópicos `Results-*`.

### Partição
Os tópicos são divididos em partições para paralelismo. Cada partição é um log ordenado e imutável. Neste projeto: 3 partições por tópico (configuração do cluster).

### Offset de Partição
A posição de uma mensagem dentro de uma partição. Os consumers registam o seu offset para saber onde ficaram. Repor o offset permite reprocessar mensagens desde qualquer ponto.

### Broker
Um servidor Kafka que armazena e serve mensagens. Neste projeto: **3 brokers** (`broker1`, `broker2`, `broker3`) para tolerância a falhas com replication-factor 3.

### Zookeeper vs KRaft
- **Zookeeper**: Coordenador tradicional para os metadados do cluster Kafka (usado no nosso cluster com `confluentinc/cp-kafka:7.5.1`)
- **KRaft**: Modo mais recente onde o Kafka gere os seus próprios metadados sem Zookeeper (usado no setup standalone)

---

## 2. Kafka Streams

### O que é o Kafka Streams?
Uma biblioteca Java para construir aplicações de processamento de streams em tempo real. Lê de tópicos de entrada, processa dados, escreve para tópicos de saída. É stateful — consegue manter agregações ao longo das mensagens.

### Abstrações principais
- **KStream**: Fluxo ilimitado de registos (cada registo é um evento)
- **KTable**: Fluxo de changelog — cada chave tem um único valor atual (como uma tabela)
- **GlobalKTable**: KTable replicada para todas as instâncias

### Operações usadas neste projeto

#### `groupByKey()` / `groupBy()`
Agrupa registos por chave antes de agregar.
- `groupByKey()` — usa a chave existente
- `groupBy()` — permite mudar a chave (ex: mudar todas as chaves para `"total_revenue"` para agregação global)

#### `aggregate()`
Acumula um valor corrente por chave. Usado para receitas, despesas, médias.
```java
.aggregate(
    () -> 0.0,                                    // inicializador
    (key, sale, aggr) -> aggr + sale.price * sale.quantity,  // agregador
    Materialized.with(Serdes.String(), Serdes.Double())
)
```
Usado em: Req #5, #6, #8, #9, #11, #12, #17

#### `reduce()`
Caso especial de aggregate — combina dois valores do mesmo tipo. Usado para encontrar o item com maior lucro (guarda o máximo).
```java
.reduce((a, b) -> a >= b ? a : b)
```
Usado em: Req #13

#### `join()` (KTable-KTable)
Combina duas KTables por chave. Usado para lucro = receita − despesas.
```java
revenueTable.join(expensesTable, (revenue, expenses) -> revenue - expenses)
```
Usado em: Req #7, #10, #12

#### `windowedBy(TimeWindows.of(Duration.ofHours(1)))`
Janela temporal tumbling — agrupa registos dentro de um intervalo de tempo fixo. Cada janela é independente. Usado para métricas da última hora.
Usado em: Req #14, #15, #16

#### Chave composta
Para agregar por livro e por país (Req #17), usa-se uma chave composta `"bookId_countryId"`:
```java
.map((k, v) -> new KeyValue<>(v.book_id + "_" + v.country_id, v))
```

---

## 2A. Análise Detalhada — Operações Streams no código real

### `aggregate()` — como funciona

Acumula um valor corrente por chave. A cada nova mensagem, o aggregator é chamado com a chave, o novo valor, e o acumulador atual.

**Req #5 — Receita por livro** (`ProjetoBase3Streams.java` linhas 212–225):
```java
KTable<String, Double> revenuePerBook = sales
    .map((k, v) -> new KeyValue<>(String.valueOf(v.book_id), v)) // muda a chave para book_id
    .groupByKey(Grouped.with(Serdes.String(), saleSerde))
    .aggregate(
        () -> 0.0,                                               // começa em 0
        (key, sale, aggr) -> aggr + (sale.price * sale.quantity), // acumula preço × qtd
        Materialized.with(Serdes.String(), Serdes.Double())
    );
```
→ Resultado: uma KTable com `book_id → receita total`. Cada vez que chega uma venda, o valor é atualizado.

**Req #8 — Receita total** (linhas 228–241):
```java
KTable<String, Double> totalRevenue = sales
    .map((k, v) -> new KeyValue<>("total_metrics", v)) // TODAS as vendas recebem a MESMA chave
    .groupByKey(...)
    .aggregate(
        () -> 0.0,
        (key, sale, aggr) -> aggr + (sale.price * sale.quantity), // soma tudo
        ...
    );
```
→ Truque: ao forçar a chave `"total_metrics"` em todos os registos, o aggregate soma-os todos numa só entrada.

---

### `groupByKey()` vs `groupBy()` — a diferença real

No código usa-se `.map()` para mudar a chave **antes** de chamar `.groupByKey()`.

```java
sales.map((k, v) -> new KeyValue<>(String.valueOf(v.book_id), v))
     .groupByKey(...)
```

Isto é equivalente a usar `groupBy()`, mas feito em dois passos. **Ambos causam reparticionamento** — o Kafka Streams cria um tópico interno para redistribuir os dados pela nova chave.

| | `groupByKey()` | `groupBy()` |
|---|---|---|
| Reparticionamento | Só se a chave mudou antes | **Sempre** |
| Eficiência | Mais eficiente | Menos eficiente |
| Uso aqui | Após `.map()` que já mudou a chave | Alternativa direta |

---

### `join()` KTable-KTable — como funciona

```java
// Req #7 — Lucro por livro (linhas 280–288)
revenuePerBook.join(
    expensesPerBook,
    (revenue, expenses) -> revenue - expenses,  // combina os dois valores
    Materialized.with(Serdes.String(), Serdes.Double())
)
```

- **KTable-KTable join**: sempre que uma das tabelas atualiza para uma chave, o join é recomputado para essa chave.
- Resultado: sempre o estado mais recente de `revenue - expenses` por livro.
- Se `expensesPerBook` ainda não tem valor para um livro, o join **não produz resultado** para esse livro (inner join por defeito).

Mesmo padrão para Req #10 (lucro total), Req #11 (média por livro), Req #12 (média global).

---

### `reduce()` — Req #13 — Livro com maior lucro

```java
// linhas 341–353
revenuePerBook
    .join(expensesPerBook, (revenue, expenses) -> revenue - expenses, ...)
    .toStream()
    .map((k, v) -> new KeyValue<>("top_profit_book", v))  // todos sob a mesma chave
    .groupByKey(...)
    .reduce((v1, v2) -> v1 >= v2 ? v1 : v2)              // guarda o máximo
```

- `reduce()` é um caso especial de `aggregate()` onde o tipo de entrada e saída são iguais.
- Aqui mantém o **maior valor de lucro** alguma vez visto.
- **Limitação**: guarda o valor máximo, não o `book_id`. Se o professor perguntar, o `top_profit_book` na BD contém o valor do lucro, não o ID do livro.

---

### `windowedBy()` — Requisitos #14, #15, #16

```java
// Req #14 — Receita última hora (linhas 357–369)
sales
    .map((k, v) -> new KeyValue<>("revenue_last_hour", v))
    .groupByKey(...)
    .windowedBy(TimeWindows.of(Duration.ofHours(1)))  // janela tumbling de 1 hora
    .aggregate(
        () -> 0.0,
        (key, sale, aggr) -> aggr + (sale.price * sale.quantity),
        ...
    )
    .toStream()
    .map((k, v) -> new KeyValue<>(k.key(), windowedMetricJson("revenue_last_hour", v)))
```

- **Tumbling window**: janelas fixas, não sobrepostas — 10:00–11:00, 11:00–12:00, etc.
- O Kafka usa o **timestamp do evento** (campo `timestamp` da mensagem), não o tempo do servidor.
- `k.key()` extrai a chave da `Windowed<String>` — necessário porque o tipo da chave muda para `Windowed<K>` após `windowedBy`.
- Cada janela começa do zero. Só conta eventos dentro daquela hora.

---

## 3. Kafka Connect

### O que é o Kafka Connect?
Uma framework para ligar o Kafka a sistemas externos sem escrever código — apenas configuração JSON.

### Source Connector
Lê de um sistema externo e escreve para o Kafka. Neste projeto: o JDBC Source lê as tabelas `book` e `country` do PostgreSQL e escreve para o tópico `DBInfo` periodicamente.

### Sink Connector
Lê do Kafka e escreve para um sistema externo. Neste projeto: 13 JDBC Sink connectors, um por tópico Results, a escrever para tabelas PostgreSQL.

### Opções de configuração principais
- `insert.mode: upsert` — insere ou atualiza com base na chave primária
- `pk.mode: record_value` — a chave primária vem do valor da mensagem
- `value.converter.schemas.enable: true` — necessário para o JDBC Sink conhecer os tipos dos campos
- `auto.create: false` — as tabelas já foram criadas pelo `create_tables.sql`

### Porquê o envelope schema+payload JSON?
O JDBC Sink Connector precisa de informação de schema para mapear os campos para as colunas da BD. Sem Schema Registry, o schema é embutido diretamente na mensagem:
```json
{
  "schema": {
    "type": "struct",
    "fields": [{"type": "int32", "field": "book_id"}, {"type": "double", "field": "revenue"}]
  },
  "payload": {"book_id": 1, "revenue": 45.0}
}
```
Este envelope é produzido pelo Kafka Streams antes de escrever para os tópicos Results.

---

## 4. Serialização / Deserialização (SerDes)

### O que são SerDes?
Serializer + Deserializer. As mensagens Kafka são bytes — os SerDes convertem entre objetos Java e bytes.

### Neste projeto
- Tópicos de entrada: strings JSON simples, deserializadas manualmente com Gson para `PurchaseEvent` / `SaleEvent`
- Tópicos de saída: strings JSON com schema+payload (pré-serializadas), usando `Serdes.String()`
- Sem Schema Registry, sem Avro/Protobuf — JSON puro

### Porquê não Avro?
O Avro requer um Schema Registry. JSON sem Schema Registry foi escolhido pela simplicidade e compatibilidade com o Kafka Connect JsonConverter.

---

## 5. Semânticas de Entrega

### At most once (no máximo uma vez)
A mensagem pode perder-se, nunca é duplicada. O producer envia e esquece (`acks=0`).

### At least once (pelo menos uma vez)
A mensagem nunca se perde mas pode ser duplicada. O producer faz retry em caso de falha. É o comportamento padrão do Kafka.

### Exactly once (exatamente uma vez)
Sem perda, sem duplicação. Requer:
- **Producer idempotente**: `enable.idempotence=true` — o Kafka elimina retries duplicados
- **Transações**: o producer agrupa os envios em transações
- **Isolation level do consumer**: `read_committed` — só lê mensagens confirmadas

Neste projeto: `acks=all` está configurado nos producers (garantia forte de durabilidade), mas exactly-once completo não foi implementado explicitamente.

---

## 6. Tolerância a Falhas — ISR, RF e Cenários de Falha

### Replication Factor (RF)

O **RF** define quantas cópias de cada partição existem no cluster.

No projeto: `replication-factor=3` → cada partição tem **3 réplicas**, uma em cada broker.

```
Partição 0 do tópico "Sales":
  broker1 → LÍDER  (serve leituras e escritas)
  broker2 → follower (réplica)
  broker3 → follower (réplica)
```

Onde está no código: `KAFKA_DEFAULT_REPLICATION_FACTOR: 3` em `docker-compose-cluster.yml` (linhas 41, 57, 72).

---

### ISR — In-Sync Replicas

**ISR** é o conjunto de réplicas que estão **sincronizadas** com o líder (não estão atrasadas).

- Só as réplicas em ISR são elegíveis para se tornarem líderes se o broker atual falhar.
- Se uma réplica fica para trás (rede lenta, reinício), é removida do ISR.
- Quando recupera, volta a sincronizar e é readmitida no ISR.

**`acks=all`** (configurado nos producers do projeto — `SaleEventProducer.java:28`, `PurchaseEventProducer.java:29`):
- O producer só considera a mensagem enviada quando **todas as réplicas em ISR** confirmaram.
- Se ISR = 3 (todos), precisas de 3 acks. Se um broker caiu e ISR = 2, precisas de 2 acks.
- Garante **durabilidade máxima** — nenhuma mensagem reconhecida se perde.

---

### Cenários de Falha — O que acontece?

#### Cenário 1: Um **Producer** cai

| Questão | Resposta |
|---------|----------|
| Dá para ler mensagens já enviadas? | ✅ Sim — já estão nos brokers, replicadas |
| Dá para escrever novas mensagens? | ❌ Não — não há ninguém a produzir |
| O Kafka Streams continua? | ✅ Sim — processa o que está nos tópicos |
| E quando o producer volta? | ✅ Retoma normalmente, não perde contexto |

> No projeto, os producers são o `PurchaseEventProducer`, `SaleEventProducer`, e o MCP tool `create_test_transactions` (Python). Se o servidor Python cair, o Kafka Streams continua a processar o que já existe.

---

#### Cenário 2: Um **Broker** cai (1 de 3)

| Questão | Resposta |
|---------|----------|
| Dá para ler? | ✅ Sim — outro broker torna-se líder das partições afetadas |
| Dá para escrever? | ✅ Sim — com `acks=all` e ISR=2 ainda funciona |
| Há perda de dados? | ❌ Não — RF=3, ficam 2 réplicas íntegras |
| O Streams reconecta? | ✅ Sim — tem os 3 brokers na lista de bootstrap servers |

```
bootstrap.servers = broker1:9092,broker2:9092,broker3:9092
```
Se `broker2` cair, o Streams liga-se ao `broker1` ou `broker3` automaticamente.

> Demo:
> ```bash
> docker stop devcontainer-broker2-1
> # sistema continua a funcionar
> docker start devcontainer-broker2-1
> ```

---

#### Cenário 3: O **Kafka Streams** cai (consumer)

| Questão | Resposta |
|---------|----------|
| Dá para ler do Kafka? | ✅ Sim — outras aplicações podem ler |
| Dá para escrever no Kafka? | ✅ Sim — producers não são afetados |
| Há perda de dados de processamento? | ❌ Não — os offsets estão guardados no Kafka |
| Quando volta, recomeça do início? | ❌ Não — retoma do último offset confirmado |

O Kafka Streams guarda os offsets dos tópicos de entrada. Quando reinicia, continua de onde parou. As mensagens que ainda não foram processadas ficam à espera nos tópicos.

---

#### Cenário 4: O **Kafka Connect** cai

| Questão | Resposta |
|---------|----------|
| O Streams continua? | ✅ Sim — escreve para os tópicos Results-* |
| Os dados chegam ao PostgreSQL? | ❌ Não — o Sink não está a consumir |
| Há perda de dados? | ❌ Não — as mensagens ficam nos tópicos Results-* |
| Quando o Connect volta? | ✅ Retoma do offset guardado, escreve tudo |

---

#### Cenário 5: Todos os brokers caem

- Sistema para completamente.
- Quando voltam: o Kafka recupera os dados do disco (armazenamento durável).
- O Zookeeper deteta a volta dos brokers e reconstrói o estado do cluster.

---

### Resumo rápido para a defesa

```
RF=3     → 3 cópias de cada partição (tolerância a 2 falhas de broker)
ISR      → conjunto de réplicas sincronizadas; só elas podem ser eleitas líder
acks=all → producer espera confirmação de todos os ISR antes de considerar enviado

Producer cai → leitura ✅, escrita ❌ (até reiniciar), Streams continua ✅
Broker cai   → leitura ✅, escrita ✅ (se ISR ≥ 1), sem perda de dados ✅
Streams cai  → retoma do offset guardado ✅, sem perda ✅
Connect cai  → dados ficam nos tópicos ✅, BD desatualizada até voltar ✅
```

---

## 7. Os 17 Requisitos

| Req | Descrição | Operação Kafka | Endpoint API |
|-----|-----------|----------------|--------------|
| #1 | Adicionar países | — (BD direta) | `POST /countries` |
| #2 | Listar países | — (BD direta) | `GET /countries` |
| #3 | Adicionar livros | — (BD direta) | `POST /books` |
| #4 | Listar livros | — (BD direta) | `GET /books` |
| #5 | Receita por livro | `aggregate()` | `GET /analytics/stats/revenue-per-book` |
| #6 | Despesas por livro | `aggregate()` | `GET /analytics/stats/expenses-per-book` |
| #7 | Lucro por livro | `join()` KTable | `GET /analytics/stats/profit-per-book` |
| #8 | Receita total | `groupBy().aggregate()` | `GET /analytics/stats/total-revenue` |
| #9 | Despesas totais | `groupBy().aggregate()` | `GET /analytics/stats/total-expenses` |
| #10 | Lucro total | `join()` KTable | `GET /analytics/stats/total-profit` |
| #11 | Média de compra por livro | `aggregate()` | `GET /analytics/stats/average-purchase-per-book` |
| #12 | Média de compra global | `groupBy().aggregate()` + `join()` | `GET /analytics/stats/average-purchase-all-books` |
| #13 | Livro com maior lucro | `reduce(max)` | `GET /analytics/stats/top-profit-book` |
| #14 | Receita última hora | `windowedBy(1h)` | `GET /analytics/stats/revenue-last-hour` |
| #15 | Despesas última hora | `windowedBy(1h)` | `GET /analytics/stats/expenses-last-hour` |
| #16 | Lucro última hora | `windowedBy(1h)` | `GET /analytics/stats/profit-last-hour` |
| #17 | País com mais vendas por livro | `aggregate()` chave composta | `GET /analytics/stats/top-country-sales-per-book` |

---

## 8. Arquitetura

```
[Agente MCP / Producers]
        ↓
   Tópicos Kafka: Sales, Purchases
        ↓
 [Kafka Streams — ProjetoBase3Streams.java]
   aggregate, join, reduce, windowedBy
        ↓
 [13 Tópicos Results-*]
        ↓
 [Kafka Connect — 13 JDBC Sinks]
        ↓
    [PostgreSQL — 6 tabelas]
        ↑
   [FastAPI REST API :8001]
        ↑
 [Servidor MCP :8002 + Agente LangChain :8000]
        ↑
     [Webapp]
```

Também: o **Kafka Connect Source** lê as tabelas `book` e `country` do PostgreSQL → tópico `DBInfo`.

---

## 9. Perguntas Prováveis na Defesa Oral

**P: Porquê usar Kafka em vez de uma REST API para calcular métricas?**  
R: O Kafka desacopla producers de consumers, processa dados em tempo real à medida que chegam os eventos, e escala horizontalmente. Calcular métricas no Kafka Streams evita queries pesadas à BD e suporta alto throughput.

**P: Qual é a diferença entre KStream e KTable?**  
R: O KStream é um fluxo ilimitado onde cada registo é um evento independente. O KTable é um fluxo de changelog onde cada chave tem um único valor atual — como uma tabela continuamente atualizada. O join entre dois KTables dá o estado combinado mais recente.

**P: Porquê precisas do envelope schema+payload JSON?**  
R: O JDBC Sink Connector do Kafka Connect precisa de informação de schema para mapear os campos para as colunas da BD. Sem Schema Registry, o schema tem de ser embutido em cada mensagem com o envelope `{"schema":{...}, "payload":{...}}`.

**P: O que é uma tumbling window?**  
R: Uma janela temporal de tamanho fixo, sem sobreposição. Ex: janela de 1 hora: 10:00–11:00, 11:00–12:00, etc. Cada evento pertence a exatamente uma janela.

**P: Como funciona a tolerância a falhas no teu setup?**  
R: 3 brokers com replication-factor 3. Cada partição está replicada em todos os brokers. Se um broker cair, outro torna-se líder e o cluster continua sem perda de dados.

**P: Para que servem os consumer groups?**  
R: Permitem que vários consumers partilhem a carga de leitura de um tópico. Cada partição é lida por exatamente um consumer do grupo. O Kafka Streams usa consumer groups internamente para distribuir partições pelas threads de processamento.

**P: Qual é a diferença entre `groupByKey()` e `groupBy()`?**  
R: `groupByKey()` agrupa usando a chave existente — mais eficiente, sem reparticionamento. `groupBy()` permite mudar a chave, mas causa sempre reparticionamento (cria um tópico interno). No código usei `.map()` para mudar a chave seguido de `groupByKey()` — é equivalente mas mais explícito.

**P: Como funciona o Agente MCP?**  
R: O MCP (Model Context Protocol) expõe funções Python como "ferramentas" que um LLM pode invocar. O agente LangChain recebe uma pergunta em linguagem natural, decide qual ferramenta chamar, executa a função e devolve o resultado. As ferramentas chamam a REST API ou o producer Kafka diretamente.

**P: O que acontece a mensagens que chegam antes de um consumer subscrever?**  
R: Por defeito, novos consumers só lêem mensagens novas. Para ler dados históricos, usa-se `--from-beginning` (define o offset para o início). Isto funciona porque o Kafka guarda as mensagens de forma durável em disco.

**P: O que é um offset de partição?**  
R: Um número sequencial que identifica cada mensagem dentro de uma partição. Os consumers registam o seu offset para saber quais as mensagens que já processaram. Repor o offset permite reproduzir mensagens.

**P: O que é o ISR e para que serve?**  
R: ISR (In-Sync Replicas) é o conjunto de réplicas sincronizadas com o líder da partição. Quando o líder falha, apenas uma réplica do ISR é eleita como novo líder — isto garante que não há perda de dados. Se uma réplica ficar para trás, é removida do ISR até recuperar.

**P: O que significa `acks=all` nos teus producers?**  
R: O producer só considera a mensagem enviada quando todas as réplicas em ISR confirmaram a receção. É a configuração mais forte — garante durabilidade máxima. Em troca, tem mais latência que `acks=1` (só o líder) ou `acks=0` (sem confirmação).

**P: Se um broker cai, continua a dar para escrever?**  
R: Sim, desde que o ISR ainda tenha réplicas suficientes. Com RF=3 e um broker em baixo, ficam 2 réplicas. Com `acks=all` e as 2 réplicas sincronizadas, os producers continuam a escrever normalmente. O Zookeeper elege um novo líder para as partições afetadas.

**P: Se o producer cai, continua a dar para ler?**  
R: Sim. As mensagens já enviadas estão armazenadas nos brokers com RF=3. Qualquer consumer (incluindo o Kafka Streams) pode continuar a lê-las. O Kafka é um sistema de armazenamento, não apenas um buffer — as mensagens persistem até ao fim do retention period (7 dias por defeito).

**P: Se o Kafka Streams cai a meio, perde-se processamento?**  
R: Não. O Streams guarda os offsets dos tópicos de entrada no Kafka. Quando reinicia, retoma exatamente do ponto onde ficou. As mensagens não processadas ficam à espera nos tópicos.

**P: Porquê é que o Req #13 guarda o valor do lucro e não o book_id?**  
R: Porque usei `reduce()` que opera sobre os valores, não as chaves. O `reduce((v1, v2) -> v1 >= v2 ? v1 : v2)` mantém o maior valor de lucro, mas a chave é sempre `"top_profit_book"`. Uma solução alternativa seria usar `aggregate()` com um objeto que guarde tanto o book_id como o valor.

**P: Porquê usas `groupByKey()` após um `.map()` e não usas `groupBy()` diretamente?**  
R: São equivalentes em resultado — ambos causam reparticionamento. Optei por fazer `.map()` explicitamente para tornar o código mais legível: fica claro que estou a mudar a chave antes de agrupar.

**P: O que acontece ao Kafka Streams quando um broker cai?**  
R: O Streams tem `bootstrap.servers=broker1:9092,broker2:9092,broker3:9092`. Se um broker cai, o cliente Kafka reconecta automaticamente para um dos outros. O Streams deteta que algumas partições mudaram de líder e reajusta os consumers internos — sem intervenção manual e sem perda de dados.

**P: Porquê criaste os tópicos Sales e Purchases manualmente?**  
R: O Kafka Streams pode criar automaticamente os seus tópicos internos (repartition, changelog), mas **não cria os tópicos de entrada** — isso é responsabilidade do operador. Se os tópicos não existirem quando o Streams arranca, falha com `UNKNOWN_TOPIC_OR_PARTITION`. Por isso há o passo explícito de criar Sales e Purchases antes de iniciar o Streams.

**P: O que é um KTable e como difere de um KStream?**  
R: Um KStream é uma sequência infinita de eventos — cada registo é independente (ex: "livro 1 vendeu 2 unidades"). Um KTable é uma vista materializada — cada chave tem um único valor atual, atualizado quando chega um novo registo com a mesma chave (ex: "livro 1 → receita total = 45.0"). O join no Req #7 usa dois KTables para calcular lucro = receita atual − despesas atuais.
