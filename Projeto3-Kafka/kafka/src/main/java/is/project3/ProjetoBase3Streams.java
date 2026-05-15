package is.project3;

import org.apache.kafka.common.serialization.Serde;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.Properties;

public class ProjetoBase3Streams {
    private static final Logger logger = LoggerFactory.getLogger(ProjetoBase3Streams.class);

    public static void main(String[] args) {
        Properties properties = new Properties();
        properties.put(StreamsConfig.APPLICATION_ID_CONFIG, "project3-analytics-streams");
        properties.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "broker1:9092");
        properties.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        properties.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        properties.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 1000);
        properties.put(StreamsConfig.CACHE_MAX_BYTES_BUFFERING_CONFIG, 0);

        StreamsBuilder builder = new StreamsBuilder();

        // Custom Serdes
        Serde<PurchaseEvent> purchaseSerde = Serdes.serdeFrom(
            new PurchaseEventSerde.PurchaseEventSerializer(),
            new PurchaseEventSerde.PurchaseEventDeserializer()
        );
        Serde<SaleEvent> saleSerde = Serdes.serdeFrom(
            new SaleEventSerde.SaleEventSerializer(),
            new SaleEventSerde.SaleEventDeserializer()
        );
        Serde<ResultEvent> resultSerde = Serdes.serdeFrom(
            new ResultEventSerde.ResultEventSerializer(),
            new ResultEventSerde.ResultEventDeserializer()
        );
        Serde<MetricEvent> metricSerde = Serdes.serdeFrom(
            new MetricEventSerde.MetricEventSerializer(),
            new MetricEventSerde.MetricEventDeserializer()
        );

        // Read input streams
        KStream<String, PurchaseEvent> purchases = builder.stream(
            "Purchases",
            Consumed.with(Serdes.String(), purchaseSerde)
        );

        KStream<String, SaleEvent> sales = builder.stream(
            "Sales",
            Consumed.with(Serdes.String(), saleSerde)
        );

        // ===== REVENUE COMPUTATIONS =====

        // Revenue per book: KStream -> KTable via groupByKey().aggregate()
        KTable<String, Double> revenuePerBook = sales
            .map((k, v) -> new KeyValue<>(String.valueOf(v.book_id), v))
            .groupByKey(Grouped.with(Serdes.String(), saleSerde))
            .aggregate(
                () -> 0.0,
                (key, sale, aggr) -> aggr + (sale.price * sale.quantity),
                Materialized.with(Serdes.String(), Serdes.Double())
            );

        revenuePerBook
            .toStream()
            .map((k, v) -> new KeyValue<>(k, new MetricEvent(k, v, System.currentTimeMillis())))
            .to("Results-revenue-per-book", Produced.with(Serdes.String(), metricSerde));

        // Total revenue: aggregate all sales
        KTable<String, Double> totalRevenue = sales
            .map((k, v) -> new KeyValue<>("total", v))
            .groupByKey(Grouped.with(Serdes.String(), saleSerde))
            .aggregate(
                () -> 0.0,
                (key, sale, aggr) -> aggr + (sale.price * sale.quantity),
                Materialized.with(Serdes.String(), Serdes.Double())
            );

        totalRevenue
            .toStream()
            .map((k, v) -> new KeyValue<>(k, new MetricEvent(k, v, System.currentTimeMillis())))
            .to("Results-total-revenue", Produced.with(Serdes.String(), metricSerde));

        // ===== EXPENSES COMPUTATIONS =====

        // Expenses per book
        KTable<String, Double> expensesPerBook = purchases
            .map((k, v) -> new KeyValue<>(String.valueOf(v.book_id), v))
            .groupByKey(Grouped.with(Serdes.String(), purchaseSerde))
            .aggregate(
                () -> 0.0,
                (key, purchase, aggr) -> aggr + (purchase.cost * purchase.quantity),
                Materialized.with(Serdes.String(), Serdes.Double())
            );

        expensesPerBook
            .toStream()
            .map((k, v) -> new KeyValue<>(k, new MetricEvent(k, v, System.currentTimeMillis())))
            .to("Results-expenses-per-book", Produced.with(Serdes.String(), metricSerde));

        // Total expenses
        KTable<String, Double> totalExpenses = purchases
            .map((k, v) -> new KeyValue<>("total", v))
            .groupByKey(Grouped.with(Serdes.String(), purchaseSerde))
            .aggregate(
                () -> 0.0,
                (key, purchase, aggr) -> aggr + (purchase.cost * purchase.quantity),
                Materialized.with(Serdes.String(), Serdes.Double())
            );

        totalExpenses
            .toStream()
            .map((k, v) -> new KeyValue<>(k, new MetricEvent(k, v, System.currentTimeMillis())))
            .to("Results-total-expenses", Produced.with(Serdes.String(), metricSerde));

        // ===== PROFIT COMPUTATIONS =====

        // Profit per book = revenue - expenses
        revenuePerBook
            .join(
                expensesPerBook,
                (revenue, expenses) -> revenue - expenses,
                Materialized.with(Serdes.String(), Serdes.Double())
            )
            .toStream()
            .map((k, v) -> new KeyValue<>(k, new MetricEvent(k, v, System.currentTimeMillis())))
            .to("Results-profit-per-book", Produced.with(Serdes.String(), metricSerde));

        // Total profit
        totalRevenue
            .join(
                totalExpenses,
                (revenue, expenses) -> revenue - expenses,
                Materialized.with(Serdes.String(), Serdes.Double())
            )
            .toStream()
            .map((k, v) -> new KeyValue<>(k, new MetricEvent(k, v, System.currentTimeMillis())))
            .to("Results-total-profit", Produced.with(Serdes.String(), metricSerde));

        // ===== AVERAGE PURCHASE COMPUTATIONS =====

        // Average purchase per book
        KTable<String, Long> purchaseCountPerBook = purchases
            .map((k, v) -> new KeyValue<>(String.valueOf(v.book_id), v))
            .groupByKey(Grouped.with(Serdes.String(), purchaseSerde))
            .count(Materialized.with(Serdes.String(), Serdes.Long()));

        expensesPerBook
            .join(
                purchaseCountPerBook,
                (expenses, count) -> count > 0 ? expenses / count : 0.0,
                Materialized.with(Serdes.String(), Serdes.Double())
            )
            .toStream()
            .map((k, v) -> new KeyValue<>(k, new MetricEvent(k, v, System.currentTimeMillis())))
            .to("Results-avg-purchase-per-book", Produced.with(Serdes.String(), metricSerde));

        // Average purchase across all books
        KTable<String, Long> purchaseCountAll = purchases
            .map((k, v) -> new KeyValue<>("all", v))
            .groupByKey(Grouped.with(Serdes.String(), purchaseSerde))
            .count(Materialized.with(Serdes.String(), Serdes.Long()));

        totalExpenses
            .join(
                purchaseCountAll,
                (expenses, count) -> count > 0 ? expenses / count : 0.0,
                Materialized.with(Serdes.String(), Serdes.Double())
            )
            .toStream()
            .map((k, v) -> new KeyValue<>(k, new MetricEvent(k, v, System.currentTimeMillis())))
            .to("Results-avg-purchase-all", Produced.with(Serdes.String(), metricSerde));

        // ===== TOP PROFIT BOOK =====
        revenuePerBook
            .join(
                expensesPerBook,
                (revenue, expenses) -> revenue - expenses,
                Materialized.with(Serdes.String(), Serdes.Double())
            )
            .toStream()
            .map((k, v) -> new KeyValue<>("top", v))
            .groupByKey(Grouped.with(Serdes.String(), Serdes.Double()))
            .reduce((v1, v2) -> v1 >= v2 ? v1 : v2)
            .toStream()
            .map((k, v) -> new KeyValue<>(k, new MetricEvent(k, v, System.currentTimeMillis())))
            .to("Results-top-profit-book", Produced.with(Serdes.String(), metricSerde));

        // ===== TIME-WINDOWED COMPUTATIONS (Last Hour) =====

        // Revenue last hour
        sales
            .map((k, v) -> new KeyValue<>("total", v))
            .groupByKey(Grouped.with(Serdes.String(), saleSerde))
            .windowedBy(TimeWindows.of(Duration.ofHours(1)))
            .aggregate(
                () -> 0.0,
                (key, sale, aggr) -> aggr + (sale.price * sale.quantity),
                Materialized.with(Serdes.String(), Serdes.Double())
            )
            .toStream()
            .map((k, v) -> new KeyValue<>(k.key(), new MetricEvent(k.key(), v, System.currentTimeMillis())))
            .to("Results-revenue-last-hour", Produced.with(Serdes.String(), metricSerde));

        // Expenses last hour
        purchases
            .map((k, v) -> new KeyValue<>("total", v))
            .groupByKey(Grouped.with(Serdes.String(), purchaseSerde))
            .windowedBy(TimeWindows.of(Duration.ofHours(1)))
            .aggregate(
                () -> 0.0,
                (key, purchase, aggr) -> aggr + (purchase.cost * purchase.quantity),
                Materialized.with(Serdes.String(), Serdes.Double())
            )
            .toStream()
            .map((k, v) -> new KeyValue<>(k.key(), new MetricEvent(k.key(), v, System.currentTimeMillis())))
            .to("Results-expenses-last-hour", Produced.with(Serdes.String(), metricSerde));

        // Profit last hour (would require joining windowed tables)

        // ===== TOP COUNTRY SALES PER BOOK =====
        sales
            .map((k, v) -> new KeyValue<>(
                v.book_id + "_" + v.country_id,
                v
            ))
            .groupByKey(Grouped.with(Serdes.String(), saleSerde))
            .aggregate(
                () -> 0.0,
                (key, sale, aggr) -> aggr + (sale.price * sale.quantity),
                Materialized.with(Serdes.String(), Serdes.Double())
            )
            .toStream()
            .map((k, v) -> new KeyValue<>(k, new MetricEvent(k, v, System.currentTimeMillis())))
            .to("Results-top-country-sales-per-book", Produced.with(Serdes.String(), metricSerde));

        KafkaStreams streams = new KafkaStreams(builder.build(), properties);
        streams.cleanUp();
        streams.start();

        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));

        logger.info("Kafka Streams application started");
    }
}
