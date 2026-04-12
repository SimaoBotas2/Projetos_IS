VMs Andre
| Records | Format | Operation       | Size (bytes) | Time (s) | Throughput (bytes/sec) | Memory Used (MB) |
| ------- | ------ | --------------- | ------------ | -------- | ---------------------- | ---------------- |
| 10,000  | XML    | Serialization   | 648,103      | 0.0937   | 6,916,572              | 4                |
| 10,000  | XML    | Deserialization | 648,103      | 0.2724   | 2,379,249              | 3                |
| 10,000  | JSON   | Serialization   | 427,945      | 0.1181   | 3,623,892              | 4                |
| 10,000  | JSON   | Deserialization | 427,945      | 0.0986   | 4,341,479              | 3                |
| 100,000 | XML    | Serialization   | 6,678,103    | 0.3681   | 18,143,189             | 26               |
| 100,000 | XML    | Deserialization | 6,678,103    | 1.0554   | 6,327,835              | 26               |
| 100,000 | JSON   | Serialization   | 4,477,945    | 0.2191   | 20,434,531             | 4                |
| 100,000 | JSON   | Deserialization | 4,477,945    | 0.2436   | 18,385,416             | 4                |
| 250,000 | XML    | Serialization   | 17,028,103   | 0.5289   | 32,192,859             | 65               |
| 250,000 | XML    | Deserialization | 17,028,103   | 1.8707   | 9,102,369              | 65               |
| 250,000 | JSON   | Serialization   | 11,527,945   | 0.3121   | 36,932,606             | 37               |
| 250,000 | JSON   | Deserialization | 11,527,945   | 0.4334   | 26,600,879             | 37               |

Container Andre
| Records | Format | Operation       | Size (bytes) | Time (s) | Throughput (bytes/sec) | Memory Used (MB) |
| ------- | ------ | --------------- | ------------ | -------- | ---------------------- | ---------------- |
| 10,000  | XML    | Serialization   | 1,037,898    | 0.01513  | 68,596,474             | 6                |
| 10,000  | XML    | Deserialization | 1,037,898    | 0.27709  | 3,745,718              | 6                |
| 10,000  | JSON   | Serialization   | 537,803      | 0.00489  | 110,019,266            | 6                |
| 10,000  | JSON   | Deserialization | 537,803      | 0.09979  | 5,389,565              | 6                |
| 100,000 | XML    | Serialization   | 10,577,898   | 0.07502  | 140,997,705            | 28               |
| 100,000 | XML    | Deserialization | 10,577,898   | 0.86357  | 12,249,044             | 10               |
| 100,000 | JSON   | Serialization   | 5,577,803    | 0.01833  | 304,243,590            | 9                |
| 100,000 | JSON   | Deserialization | 5,577,803    | 0.19719  | 28,286,473             | 9                |
| 250,000 | XML    | Serialization   | 26,777,898   | 0.13051  | 205,179,959            | 171              |
| 250,000 | XML    | Deserialization | 26,777,898   | 1.23604  | 21,664,252             | 171              |
| 250,000 | JSON   | Serialization   | 14,277,803   | 0.05026  | 284,050,722            | 85               |
| 250,000 | JSON   | Deserialization | 14,277,803   | 0.28454  | 50,178,611             | 81               |

