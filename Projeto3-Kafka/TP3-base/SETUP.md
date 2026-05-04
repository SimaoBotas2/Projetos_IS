# Setup do Projeto Kafka - TP3

## Pré-requisitos
- Docker & Docker Compose instalados
- Workspace aberto em VS Code com Dev Container (opcional, mas recomendado)

---

## 1. Arrancar os Containers

A partir da raiz do projeto (`TP3-base/`):

```bash
cd .devcontainer
docker compose -f docker-compose-standalone.yml up -d --build
```

Isto arranca:
- **database**: PostgreSQL (porta 5432)
- **broker1**: Apache Kafka (porta 29092 externos, 9092 internos)
- **connect**: Kafka Connect (porta 8083)
- **command-line**: Container para correr comandos e aplicações

Verificar status:
```bash
docker compose -f docker-compose-standalone.yml ps
```

---

## 2. Entrar no Container `command-line`

```bash
docker compose -f docker-compose-standalone.yml exec command-line bash
```

Todos os comandos seguintes correm **dentro deste container**.

---

## 3. Setup dos Connectors JDBC

Dentro do container:

```bash
cd /workspace/config
./post_connectors.sh
```

Isto registra dois conectores:
- **Source**: Lê da tabela `suppliers` (PostgreSQL) → Tópico `project3fromDB`
- **Sink**: Escreve para PostgreSQL a partir de tópicos Kafka

Verificar conectores:
```bash
curl -X GET http://connect:8083/connectors/
```

---

## 4. Compilar o Projeto Maven

Dentro do container:

```bash
cd /workspace
mvn clean package
```

Isto gera `target/project3-0.0.1-SNAPSHOT.jar` com todas as dependências (Kafka Streams, Kafka Clients, GSON, etc).

---

## 5. Verificar Tópicos Kafka

Dentro do container:

```bash
kafka-topics.sh --bootstrap-server broker1:9092 --list
```

Deves ver tópicos criados pelos conectores (ex: `project3fromDB`).

---

## 6. Correr Producers

Dentro do container, após compilação:

```bash
cd /workspace
java -cp target/project3-0.0.1-SNAPSHOT.jar SockPurchasesProducer
```

(Substitui `SockPurchasesProducer` pelo nome real da classe producer no código)

---

## 7. Correr Kafka Streams

Dentro do container:

```bash
cd /workspace
java -cp target/project3-0.0.1-SNAPSHOT.jar Proje3Streams
```

---

## 8. Consumir Mensagens (Verificação)

Dentro do container, em outro terminal/sessão:

```bash
kafka-console-consumer.sh --bootstrap-server broker1:9092 --topic <NOME_TOPICO> --from-beginning
```

Exemplo:
```bash
kafka-console-consumer.sh --bootstrap-server broker1:9092 --topic Proj3SockPurchasesTopic --from-beginning
```

---

## 9. Parar os Containers

Fora do container (no host):

```bash
cd .devcontainer
docker compose -f docker-compose-standalone.yml down
```

---

## 10. Limpar Tudo (Volumes Inclusos)

```bash
cd .devcontainer
docker compose -f docker-compose-standalone.yml down -v
```

---

## Notas Importantes

- **Host Docker**: Dentro dos containers, os serviços comunicam por nomes internos (`broker1:9092`, `connect:8083`, `database:5432`).
- **Sem classes Java ainda**: O projeto não tem `src/main/java` neste momento. Adiciona as classes producers e streams conforme necessário.
- **PostgreSQL**: Arranca com tabela `suppliers` já criada (definida em `sql/create_tables.sql`).
- **Kafka Connect JARs**: Estão em `lib/` e são montados automaticamente no container.

---

## Troubleshooting

**Erro: `connect:8083 refused`**
→ Verifica se estás a correr dentro do container `command-line` (não no host Windows).

**Erro: `Cannot find class X`**
→ Compila com `mvn clean package` e verifica se a classe existe em `src/main/java`.

**Erro: `Tópico não existe`**
→ Corre `./post_connectors.sh` novamente ou cria manualmente:
```bash
kafka-topics.sh --bootstrap-server broker1:9092 --create --topic <NOME> --partitions 1 --replication-factor 1
```
