# Teste de Performance - Docker

Este diretório contém os scripts para testar serialização/desserialização em XML e JSON com diferentes tamanhos de dataset.

## Quick Start

### 1. Testar XML com 10.000 registos
```bash
cd Containers/setup
docker-compose up --build receiver sender-xml-10k
```

### 2. Testar JSON com 10.000 registos
```bash
cd Containers/setup
docker-compose up --build receiver-json sender-json-10k
```

### 3. Testar XML com 100.000 registos
```bash
cd Containers/setup
docker-compose up --build receiver sender-xml-100k
```

### 4. Testar JSON com 500.000 registos
```bash
cd Containers/setup
docker-compose up --build receiver-json sender-json-500k
```

## Estrutura

```
Containers/
├── setup/
│   ├── docker-compose.yml    # Orquestração de containers
│   ├── Dockerfile            # Para serviços XML (Java 8)
│   ├── Dockerfile.json       # Para serviços JSON (Java 17 + Maven + Jackson)
│   └── DOCKER_SETUP.md       # Documentação detalhada
├── src/                       # Código XML (Java 8)
│   ├── ClassPackage.java
│   ├── Receiver.java
│   ├── Sender.java
│   └── Student.java
└── json/                      # Código JSON (Java 17)
    ├── src/
    │   ├── ClassPackage.java
    │   ├── Receiver.java
    │   ├── RootWrapper.java
    │   ├── Sender.java
    │   └── Student.java
    └── pom.xml              # Dependências Maven (Jackson)
```

## O que foi atualizado

✅ **Sender.java (XML e JSON)** - Agora aceita parâmetro `RECORD_COUNT`:
- Padrão: 10.000 registos
- Via argumento: `java Sender host port 100000`
- Via variável de ambiente: `export RECORD_COUNT=500000`

✅ **docker-compose.yml** - 6 serviços Sender com tamanhos diferentes:
- XML: 10k, 100k, 500k
- JSON: 10k, 100k, 500k

✅ **Limites de memória** - Aumentados conforme dataset:
- 10k: 512MB
- 100k: 1GB
- 500k: 2GB

## Monitorar

Cada serviço exibe na saída:
- Número de registos enviados/recebidos
- Tamanho em bytes
- Tempo de transmissão (segundos)
- Throughput (MB/s)

Exemplo de saída:
```
Records sent: 100000
Sent bytes: 8547392
Send time (sec): 0.245
Send throughput (bytes/sec): 34881000.0
```

## Notas

- Os containers são removidos após execução (não persistem dados)
- Para persistência, use `docker-compose down -v` para limpar volumes
- Cada teste é independente - escolha um tamanho por execução
