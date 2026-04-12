# Resultados - Benchmarks XML vs JSON

| Records | Format | Operation       | Size (bytes) | Time (s) | Throughput (bytes/sec) | Memory Used (MB) |
|---------|--------|-----------------|-------------|----------|------------------------|------------------|
| 10,000  | XML    | Serialization   | 1,037,898   | 0.0186   | 55,790,000             | 6                |
| 10,000  | XML    | Deserialization | 1,037,898   | 0.4164   | 2,490,000              | 6                |
| 10,000  | JSON   | Serialization   | 537,803     | 0.0475   | 11,310,000             | 6                |
| 10,000  | JSON   | Deserialization | 537,803     | 0.2043   | 2,630,000              | 6                |
| 100,000 | XML    | Serialization   | 10,577,898  | 0.1848   | 57,250,000             | 28               |
| 100,000 | XML    | Deserialization | 10,577,898  | 1.1046   | 9,580,000              | 10               |
| 100,000 | JSON   | Serialization   | 5,577,803   | 0.0841   | 66,340,000             | 9                |
| 100,000 | JSON   | Deserialization | 5,577,803   | 0.3237   | 17,230,000             | 9                |
| 250,000 | XML    | Serialization   | 26,777,898  | 0.3491   | 76,720,000             | 171              |
| 250,000 | XML    | Deserialization | 26,777,898  | 2.2262   | 12,030,000             | 171              |
| 250,000 | JSON   | Serialization   | 14,277,803  | 0.1569   | 91,030,000             | 85               |
| 250,000 | JSON   | Deserialization | 14,277,803  | 0.3810   | 37,470,000             | 81               |
