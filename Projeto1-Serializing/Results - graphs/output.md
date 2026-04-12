# Diferenças Percentuais: Containers vs VMs

Percentual de diferença calculado como: `((Container - VM) / VM) * 100`

## XML

### 10,000 Registos

#### Serialization

| Métrica | VM | Container | Diferença % |
|---------|----|-----------|-----------|
| Size (bytes) | 648103.00 | 1037898.00 | +60.14% |
| Time (s) | 0.09 | 0.02 | -83.85% |
| Throughput (bytes/sec) | 6916572.00 | 68596474.00 | +891.77% |
| Memory Used (MB) | 4.00 | 6.00 | +50.00% |

#### Deserialization

| Métrica | VM | Container | Diferença % |
|---------|----|-----------|-----------|
| Size (bytes) | 648103.00 | 1037898.00 | +60.14% |
| Time (s) | 0.27 | 0.28 | +1.72% |
| Throughput (bytes/sec) | 2379249.00 | 3745718.00 | +57.43% |
| Memory Used (MB) | 3.00 | 6.00 | +100.00% |

### 100,000 Registos

#### Serialization

| Métrica | VM | Container | Diferença % |
|---------|----|-----------|-----------|
| Size (bytes) | 6678103.00 | 10577898.00 | +58.40% |
| Time (s) | 0.37 | 0.08 | -79.62% |
| Throughput (bytes/sec) | 18143189.00 | 140997705.00 | +677.14% |
| Memory Used (MB) | 26.00 | 28.00 | +7.69% |

#### Deserialization

| Métrica | VM | Container | Diferença % |
|---------|----|-----------|-----------|
| Size (bytes) | 6678103.00 | 10577898.00 | +58.40% |
| Time (s) | 1.06 | 0.86 | -18.18% |
| Throughput (bytes/sec) | 6327835.00 | 12249044.00 | +93.57% |
| Memory Used (MB) | 26.00 | 10.00 | -61.54% |

### 250,000 Registos

#### Serialization

| Métrica | VM | Container | Diferença % |
|---------|----|-----------|-----------|
| Size (bytes) | 17028103.00 | 26777898.00 | +57.26% |
| Time (s) | 0.53 | 0.13 | -75.32% |
| Throughput (bytes/sec) | 32192859.00 | 205179959.00 | +537.35% |
| Memory Used (MB) | 65.00 | 171.00 | +163.08% |

#### Deserialization

| Métrica | VM | Container | Diferença % |
|---------|----|-----------|-----------|
| Size (bytes) | 17028103.00 | 26777898.00 | +57.26% |
| Time (s) | 1.87 | 1.24 | -33.93% |
| Throughput (bytes/sec) | 9102369.00 | 21664252.00 | +138.01% |
| Memory Used (MB) | 65.00 | 171.00 | +163.08% |

## JSON

### 10,000 Registos

#### Serialization

| Métrica | VM | Container | Diferença % |
|---------|----|-----------|-----------|
| Size (bytes) | 427945.00 | 537803.00 | +25.67% |
| Time (s) | 0.12 | 0.00 | -95.86% |
| Throughput (bytes/sec) | 3623892.00 | 110019266.00 | +2935.94% |
| Memory Used (MB) | 4.00 | 6.00 | +50.00% |

#### Deserialization

| Métrica | VM | Container | Diferença % |
|---------|----|-----------|-----------|
| Size (bytes) | 427945.00 | 537803.00 | +25.67% |
| Time (s) | 0.10 | 0.10 | +1.21% |
| Throughput (bytes/sec) | 4341479.00 | 5389565.00 | +24.14% |
| Memory Used (MB) | 3.00 | 6.00 | +100.00% |

### 100,000 Registos

#### Serialization

| Métrica | VM | Container | Diferença % |
|---------|----|-----------|-----------|
| Size (bytes) | 4477945.00 | 5577803.00 | +24.56% |
| Time (s) | 0.22 | 0.02 | -91.63% |
| Throughput (bytes/sec) | 20434531.00 | 304243590.00 | +1388.87% |
| Memory Used (MB) | 4.00 | 9.00 | +125.00% |

#### Deserialization

| Métrica | VM | Container | Diferença % |
|---------|----|-----------|-----------|
| Size (bytes) | 4477945.00 | 5577803.00 | +24.56% |
| Time (s) | 0.24 | 0.20 | -19.05% |
| Throughput (bytes/sec) | 18385416.00 | 28286473.00 | +53.85% |
| Memory Used (MB) | 4.00 | 9.00 | +125.00% |

### 250,000 Registos

#### Serialization

| Métrica | VM | Container | Diferença % |
|---------|----|-----------|-----------|
| Size (bytes) | 11527945.00 | 14277803.00 | +23.85% |
| Time (s) | 0.31 | 0.05 | -83.90% |
| Throughput (bytes/sec) | 36932606.00 | 284050722.00 | +669.11% |
| Memory Used (MB) | 37.00 | 85.00 | +129.73% |

#### Deserialization

| Métrica | VM | Container | Diferença % |
|---------|----|-----------|-----------|
| Size (bytes) | 11527945.00 | 14277803.00 | +23.85% |
| Time (s) | 0.43 | 0.28 | -34.35% |
| Throughput (bytes/sec) | 26600879.00 | 50178611.00 | +88.64% |
| Memory Used (MB) | 37.00 | 81.00 | +118.92% |

## Resumo Geral

| Métrica | VM Média | Container Média | Diferença % |
|---------|----------|-----------------|----------|
| Time (s) | 0.47 | 0.27 | -42.07% |
| Throughput (bytes/sec) | 15448406.33 | 102883448.25 | +565.98% |
| Memory Used (MB) | 23.17 | 49.00 | +111.51% |

## Resumo Geral por Operação

### Serialization

| Métrica | VM Média | Container Média | Diferença % |
|---------|----------|-----------------|----------|
| Time (s) | 0.27 | 0.05 | -82.06% |
| Throughput (bytes/sec) | 19707274.83 | 185514619.33 | +841.35% |
| Memory Used (MB) | 23.33 | 50.83 | +117.86% |

### Deserialization

| Métrica | VM Média | Container Média | Diferença % |
|---------|----------|-----------------|----------|
| Time (s) | 0.66 | 0.49 | -25.56% |
| Throughput (bytes/sec) | 11189537.83 | 20252277.17 | +80.99% |
| Memory Used (MB) | 23.00 | 47.17 | +105.07% |

