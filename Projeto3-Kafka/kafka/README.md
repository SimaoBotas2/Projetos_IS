1. Run post_connectors.sh (inside command-line container, from /workspace/config)
2. Run producers (PurchaseEventProducer and SaleEventProducer) or use MCP tools
3. Run ProjetoBase3Streams

Checks:
1. check topics:   kafka-topics.sh --bootstrap-server broker1:9092 --list
2. see data in DB: psql -U postgres -d project3 -c "SELECT * FROM revenue_by_book;"
3. watch results:  kafka-console-consumer.sh --bootstrap-server broker1:9092 --topic Results-revenue-per-book --from-beginning
