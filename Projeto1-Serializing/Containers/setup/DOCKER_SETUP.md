# Docker Compose com JSON e XML

Este docker-compose configurado para rodar serviços de comunicação com serialização em **XML** e **JSON**, com suporte para diferentes tamanhos de dataset (10k, 100k, 500k registos).

## Estrutura

### Serviços Base
- **receiver**: Servidor que recebe dados XML pela porta 5000
- **receiver-json**: Servidor que recebe dados JSON pela porta 5001

### Serviços Sender (XML, 3 tamanhos)
- **sender-xml-10k**: Envia 10.000 registos XML
- **sender-xml-100k**: Envia 100.000 registos XML
- **sender-xml-500k**: Envia 500.000 registos XML

### Serviços Sender (JSON, 3 tamanhos)
- **sender-json-10k**: Envia 10.000 registos JSON
- **sender-json-100k**: Envia 100.000 registos JSON
- **sender-json-500k**: Envia 500.000 registos JSON

## Como usar

### XML - Testar 10k registos
```bash
docker-compose -f setup/docker-compose.yml up --build receiver sender-xml-10k
```

### XML - Testar 100k registos
```bash
docker-compose -f setup/docker-compose.yml up --build receiver sender-xml-100k
```

### XML - Testar 500k registos
```bash
docker-compose -f setup/docker-compose.yml up --build receiver sender-xml-500k
```

### JSON - Testar 10k registos
```bash
docker-compose -f setup/docker-compose.yml up --build receiver-json sender-json-10k
```

### JSON - Testar 100k registos
```bash
docker-compose -f setup/docker-compose.yml up --build receiver-json sender-json-100k
```

### JSON - Testar 500k registos
```bash
docker-compose -f setup/docker-compose.yml up --build receiver-json sender-json-500k
```

### Executar tudo simultaneamente (XML 10k + JSON 10k)
```bash
docker-compose -f setup/docker-compose.yml up --build receiver sender-xml-10k receiver-json sender-json-10k
```

### Parar os serviços
```bash
docker-compose -f setup/docker-compose.yml down
```

## Notas
- O XML usa Java 8 (JAXB já incluído no JDK)
- O JSON usa Java 17 com dependências Jackson (incluindo Maven no container)
- Cada serviço tem limites de CPU e memória:
  - **10k**: 512M máximo
  - **100k**: 1G máximo
  - **500k**: 2G máximo
- Os serviços dependem um do outro (sender depende do receiver)
- O tamanho é passado via variável de ambiente `RECORD_COUNT`
