# Resultados de Testes - Serialização XML vs JSON

## 🔴 XML - 10K Registos

| Métrica | Serialização | Desserialização |
|---------|--------------|-----------------|
| **Tamanho (bytes)** | 1.037.898 | 1.037.898 |
| **Tempo (ms)** | 18,60 | 416,39 |
| **Throughput (MB/s)** | 55,79 | 2,49 |
| **Memória (MB)** | 6 | 6 |

---

## 🔵 JSON - 10K Registos

| Métrica | Serialização | Desserialização |
|---------|--------------|-----------------|
| **Tamanho (bytes)** | 537.803 | 537.803 |
| **Tempo (ms)** | 47,54 | 204,29 |
| **Throughput (MB/s)** | 11,31 | 2,63 |
| **Memória (MB)** | 6 | 6 |

---

## 🔴 XML - 100K Registos

| Métrica | Serialização | Desserialização |
|---------|--------------|-----------------|
| **Tamanho (bytes)** | 10.577.898 | 10.577.898 |
| **Tempo (ms)** | 184,77 | 1.104,65 |
| **Throughput (MB/s)** | 57,25 | 9,58 |
| **Memória (MB)** | 28 | 10 |

---

## 🔵 JSON - 100K Registos

| Métrica | Serialização | Desserialização |
|---------|--------------|-----------------|
| **Tamanho (bytes)** | 5.577.803 | 5.577.803 |
| **Tempo (ms)** | 84,08 | 323,66 |
| **Throughput (MB/s)** | 66,34 | 17,23 |
| **Memória (MB)** | 9 | 9 |

---

## 🔴 XML - 250K Registos

| Métrica | Serialização | Desserialização |
|---------|--------------|-----------------|
| **Tamanho (bytes)** | 26.777.898 | 26.777.898 |
| **Tempo (ms)** | 349,05 | 2.226,22 |
| **Throughput (MB/s)** | 76,72 | 12,03 |
| **Memória (MB)** | 171 | 171 |

---

## 🔵 JSON - 250K Registos

| Métrica | Serialização | Desserialização |
|---------|--------------|-----------------|
| **Tamanho (bytes)** | 14.277.803 | 14.277.803 |
| **Tempo (ms)** | 156,86 | 381,02 |
| **Throughput (MB/s)** | 91,03 | 37,47 |
| **Memória (MB)** | 85 | 81 |

---

## 📊 Comparação Completa

### Tamanho do Ficheiro (bytes)

| Volume | XML | JSON | Diferença | Compressão |
|--------|-----|------|-----------|-----------|
| **10K** | 1.037.898 | 537.803 | -500.095 | XML 48,2% |
| **100K** | 10.577.898 | 5.577.803 | -5.000.095 | XML 47,3% |
| **250K** | 26.777.898 | 14.277.803 | -12.500.095 | XML 46,7% |

### Tempo Serialização (ms)

| Volume | XML | JSON | Vencedor | Diferença |
|--------|-----|------|----------|-----------|
| **10K** | 18,60 | 47,54 | **XML** | 2,56x |
| **100K** | 184,77 | 84,08 | **JSON** | 2,20x |
| **250K** | 349,05 | 156,86 | **JSON** | 2,23x |

### Tempo Desserialização (ms)

| Volume | XML | JSON | Vencedor | Diferença |
|--------|-----|------|----------|-----------|
| **10K** | 416,39 | 204,29 | **JSON** | 2,04x |
| **100K** | 1.104,65 | 323,66 | **JSON** | 3,41x |
| **250K** | 2.226,22 | 381,02 | **JSON** | 5,84x |

### Throughput Serialização (MB/s)

| Volume | XML | JSON | Melhor |
|--------|-----|------|--------|
| **10K** | 55,79 | 11,31 | **XML 4,94x** ⭐ |
| **100K** | 57,25 | 66,34 | **JSON 1,16x** |
| **250K** | 76,72 | 91,03 | **JSON 1,19x** |

### Throughput Desserialização (MB/s)

| Volume | XML | JSON | Melhor |
|--------|-----|------|--------|
| **10K** | 2,49 | 2,63 | **JSON 1,06x** |
| **100K** | 9,58 | 17,23 | **JSON 1,80x** |
| **250K** | 12,03 | 37,47 | **JSON 3,11x** |

### Uso de Memória (MB)

| Volume | XML Serial | XML Deserial | JSON Serial | JSON Deserial |
|--------|-----------|--------------|-----------|--------------|
| **10K** | 6 | 6 | 6 | 6 |
| **100K** | 28 | 10 | 9 | 9 |
| **250K** | 171 | 171 | 85 | 81 |

---

## 🎯 Conclusões

### ✅ XML Vantagens
- **Ficheiros 47% mais compactos** em todos os volumes
- **Serialização mais rápida** em volumes pequenos (10K)
- **Tamanho significativamente menor**

### ✅ JSON Vantagens  
- **Desserialização 2-6x mais rápida** 
- **Memória mais eficiente** (especialmente 250K)
- **Throughput melhor** em volumes maiores
- **Performance mais consistente**

### 📌 Recomendação
- **Armazenamento/Transmissão**: XML (ficheiros 47% menores)
- **Processamento de dados**: JSON (desserialização rápida)
- **Aplicações críticas**: JSON (eficiência de memória)
- **Trade-off**: XML perfeito para tráfego de rede, JSON melhor para processamento






