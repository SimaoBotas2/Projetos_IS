package is.project3;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
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

    // ─── Schema+Payload builders ──────────────────────────────────────────────

    /**
     * Produces {"schema":{book_id:int32, <valueField>:float64}, "payload":{...}}
     * for tables: revenue_by_book, expenses_by_book, profit_by_book, average_purchase_by_book
     */
    private static String bookMetricJson(String valueField, int bookId, double value) {
        JsonObject schema = new JsonObject();
        schema.addProperty("type", "struct");
        schema.addProperty("optional", false);

        JsonArray fields = new JsonArray();

        JsonObject f1 = new JsonObject();
        f1.addProperty("type", "int32");
        f1.addProperty("optional", false);
        f1.addProperty("field", "book_id");
        fields.add(f1);

        JsonObject f2 = new JsonObject();
        f2.addProperty("type", "double");
        f2.addProperty("optional", false);
        f2.addProperty("field", valueField);
        fields.add(f2);

        schema.add("fields", fields);

        JsonObject payload = new JsonObject();
        payload.addProperty("book_id", bookId);
        payload.addProperty(valueField, value);

        JsonObject envelope = new JsonObject();
        envelope.add("schema", schema);
        envelope.add("payload", payload);
        return envelope.toString();
    }

    /**
     * Produces {"schema":{metric_name:string, metric_value:float64}, "payload":{...}}
     * for table: total_metrics
     */
    private static String totalMetricJson(String metricName, double value) {
        JsonObject schema = new JsonObject();
        schema.addProperty("type", "struct");
        schema.addProperty("optional", false);

        JsonArray fields = new JsonArray();

        JsonObject f1 = new JsonObject();
        f1.addProperty("type", "string");
        f1.addProperty("optional", false);
        f1.addProperty("field", "metric_name");
        fields.add(f1);

        JsonObject f2 = new JsonObject();
        f2.addProperty("type", "double");
        f2.addProperty("optional", false);
        f2.addProperty("field", "metric_value");
        fields.add(f2);

        schema.add("fields", fields);

        JsonObject payload = new JsonObject();
        payload.addProperty("metric_name", metricName);
        payload.addProperty("metric_value", value);

        JsonObject envelope = new JsonObject();
        envelope.add("schema", schema);
        envelope.add("payload", payload);
        return envelope.toString();
    }

    /**
     * Produces {"schema":{metric_type:string, metric_value:float64}, "payload":{...}}
     * for table: time_window_metrics
     */
    private static String windowedMetricJson(String metricType, double value) {
        JsonObject schema = new JsonObject();
        schema.addProperty("type", "struct");
        schema.addProperty("optional", false);

        JsonArray fields = new JsonArray();

        JsonObject f1 = new JsonObject();
        f1.addProperty("type", "string");
        f1.addProperty("optional", false);
        f1.addProperty("field", "metric_type");
        fields.add(f1);

        JsonObject f2 = new JsonObject();
        f2.addProperty("type", "double");
        f2.addProperty("optional", false);
        f2.addProperty("field", "metric_value");
        fields.add(f2);

        schema.add("fields", fields);

        JsonObject payload = new JsonObject();
        payload.addProperty("metric_type", metricType);
        payload.addProperty("metric_value", value);

        JsonObject envelope = new JsonObject();
        envelope.add("schema", schema);
        envelope.add("payload", payload);
        return envelope.toString();
    }

    /**
     * Produces {"schema":{book_id:int32, country_id:int32, revenue:float64}, "payload":{...}}
     * for table: best_performing_by_country
     * key format expected: "bookId_countryId" e.g. "1_3"
     */
    private static String countryMetricJson(String compositeKey, double revenue) {
        String[] parts = compositeKey.split("_");
        int bookId = Integer.parseInt(parts[0]);
        int countryId = Integer.parseInt(parts[1]);

        JsonObject schema = new JsonObject();
        schema.addProperty("type", "struct");
        schema.addProperty("optional", false);

        JsonArray fields = new JsonArray();

        JsonObject f1 = new JsonObject();
        f1.addProperty("type", "int32");
        f1.addProperty("optional", false);
        f1.addProperty("field", "book_id");
        fields.add(f1);

        JsonObject f2 = new JsonObject();
        f2.addProperty("type", "int32");
        f2.addProperty("optional", false);
        f2.addProperty("field", "country_id");
        fields.add(f2);

        JsonObject f3 = new JsonObject();
        f3.addProperty("type", "double");
        f3.addProperty("optional", false);
        f3.addProperty("field", "revenue");
        fields.add(f3);

        schema.add("fields", fields);

        JsonObject payload = new JsonObject();
        payload.addProperty("book_id", bookId);
        payload.addProperty("country_id", countryId);
        payload.addProperty("revenue", revenue);

        JsonObject envelope = new JsonObject();
        envelope.add("schema", schema);
        envelope.add("payload", payload);
        return envelope.toString();
    }

    // ─── Main ─────────────────────────────────────────────────────────────────

    public static void main(String[] args) {
        Properties properties = new Properties();
        properties.put(StreamsConfig.APPLICATION_ID_CONFIG, "project3-analytics-streams");
        properties.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "broker1:9092");
        properties.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        properties.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        properties.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 1000);
        properties.put(StreamsConfig.CACHE_MAX_BYTES_BUFFERING_CONFIG, 0);
        // Skip malformed/legacy messages instead of crashing
        properties.put(StreamsConfig.DEFAULT_DESERIALIZATION_EXCEPTION_HANDLER_CLASS_CONFIG,
            org.apache.kafka.streams.errors.LogAndContinueExceptionHandler.class);

        StreamsBuilder builder = new StreamsBuilder();

        // Custom Serdes for input topics
        Serde<PurchaseEvent> purchaseSerde = Serdes.serdeFrom(
            new PurchaseEventSerde.PurchaseEventSerializer(),
            new PurchaseEventSerde.PurchaseEventDeserializer()
        );
        Serde<SaleEvent> saleSerde = Serdes.serdeFrom(
            new SaleEventSerde.SaleEventSerializer(),
            new SaleEventSerde.SaleEventDeserializer()
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

        // Revenue per book: sum of (price * quantity) grouped by book_id
        KTable<String, Double> revenuePerBook = sales
            .map((k, v) -> new KeyValue<>(String.valueOf(v.book_id), v))
            .groupByKey(Grouped.with(Serdes.String(), saleSerde))
            .aggregate(
                () -> 0.0,
                (key, sale, aggr) -> aggr + (sale.price * sale.quantity),
                Materialized.with(Serdes.String(), Serdes.Double())
            );

        // Req #5 — revenue per book → revenue_by_book
        revenuePerBook
            .toStream()
            .map((k, v) -> new KeyValue<>(k, bookMetricJson("revenue", Integer.parseInt(k), v)))
            .to("Results-revenue-per-book", Produced.with(Serdes.String(), Serdes.String()));

        // Total revenue: aggregate all sales under key "total_revenue"
        KTable<String, Double> totalRevenue = sales
            .map((k, v) -> new KeyValue<>("total_revenue", v))
            .groupByKey(Grouped.with(Serdes.String(), saleSerde))
            .aggregate(
                () -> 0.0,
                (key, sale, aggr) -> aggr + (sale.price * sale.quantity),
                Materialized.with(Serdes.String(), Serdes.Double())
            );

        // Req #8 — total revenue → total_metrics
        totalRevenue
            .toStream()
            .map((k, v) -> new KeyValue<>(k, totalMetricJson("total_revenue", v)))
            .to("Results-total-revenue", Produced.with(Serdes.String(), Serdes.String()));

        // ===== EXPENSES COMPUTATIONS =====

        // Expenses per book: sum of (cost * quantity) grouped by book_id
        KTable<String, Double> expensesPerBook = purchases
            .map((k, v) -> new KeyValue<>(String.valueOf(v.book_id), v))
            .groupByKey(Grouped.with(Serdes.String(), purchaseSerde))
            .aggregate(
                () -> 0.0,
                (key, purchase, aggr) -> aggr + (purchase.cost * purchase.quantity),
                Materialized.with(Serdes.String(), Serdes.Double())
            );

        // Req #6 — expenses per book → expenses_by_book
        expensesPerBook
            .toStream()
            .map((k, v) -> new KeyValue<>(k, bookMetricJson("expenses", Integer.parseInt(k), v)))
            .to("Results-expenses-per-book", Produced.with(Serdes.String(), Serdes.String()));

        // Total expenses
        KTable<String, Double> totalExpenses = purchases
            .map((k, v) -> new KeyValue<>("total_expenses", v))
            .groupByKey(Grouped.with(Serdes.String(), purchaseSerde))
            .aggregate(
                () -> 0.0,
                (key, purchase, aggr) -> aggr + (purchase.cost * purchase.quantity),
                Materialized.with(Serdes.String(), Serdes.Double())
            );

        // Req #9 — total expenses → total_metrics
        totalExpenses
            .toStream()
            .map((k, v) -> new KeyValue<>(k, totalMetricJson("total_expenses", v)))
            .to("Results-total-expenses", Produced.with(Serdes.String(), Serdes.String()));

        // ===== PROFIT COMPUTATIONS =====

        // Req #7 — profit per book = revenue - expenses → profit_by_book
        revenuePerBook
            .join(
                expensesPerBook,
                (revenue, expenses) -> revenue - expenses,
                Materialized.with(Serdes.String(), Serdes.Double())
            )
            .toStream()
            .map((k, v) -> new KeyValue<>(k, bookMetricJson("profit", Integer.parseInt(k), v)))
            .to("Results-profit-per-book", Produced.with(Serdes.String(), Serdes.String()));

        // Req #10 — total profit → total_metrics
        totalRevenue
            .join(
                totalExpenses,
                (revenue, expenses) -> revenue - expenses,
                Materialized.with(Serdes.String(), Serdes.Double())
            )
            .toStream()
            .map((k, v) -> new KeyValue<>(k, totalMetricJson("total_profit", v)))
            .to("Results-total-profit", Produced.with(Serdes.String(), Serdes.String()));

        // ===== AVERAGE PURCHASE COMPUTATIONS =====

        // Purchase count per book (for average)
        KTable<String, Long> purchaseCountPerBook = purchases
            .map((k, v) -> new KeyValue<>(String.valueOf(v.book_id), v))
            .groupByKey(Grouped.with(Serdes.String(), purchaseSerde))
            .count(Materialized.with(Serdes.String(), Serdes.Long()));

        // Req #11 — average purchase per book → average_purchase_by_book
        expensesPerBook
            .join(
                purchaseCountPerBook,
                (expenses, count) -> count > 0 ? expenses / count : 0.0,
                Materialized.with(Serdes.String(), Serdes.Double())
            )
            .toStream()
            .map((k, v) -> new KeyValue<>(k, bookMetricJson("average_amount", Integer.parseInt(k), v)))
            .to("Results-avg-purchase-per-book", Produced.with(Serdes.String(), Serdes.String()));

        // Purchase count across all books (for global average)
        KTable<String, Long> purchaseCountAll = purchases
            .map((k, v) -> new KeyValue<>("average_purchase", v))
            .groupByKey(Grouped.with(Serdes.String(), purchaseSerde))
            .count(Materialized.with(Serdes.String(), Serdes.Long()));

        // Req #12 — average purchase all items → total_metrics
        totalExpenses
            .join(
                purchaseCountAll,
                (expenses, count) -> count > 0 ? expenses / count : 0.0,
                Materialized.with(Serdes.String(), Serdes.Double())
            )
            .toStream()
            .map((k, v) -> new KeyValue<>(k, totalMetricJson("average_purchase", v)))
            .to("Results-avg-purchase-all", Produced.with(Serdes.String(), Serdes.String()));

        // ===== TOP PROFIT BOOK (Req #13) =====
        // Reduce to find the book with highest profit value
        // NOTE: this stores the MAX profit value; the book_id is lost in reduce.
        // We store it under metric_name="top_profit_book" in total_metrics.
        revenuePerBook
            .join(
                expensesPerBook,
                (revenue, expenses) -> revenue - expenses,
                Materialized.with(Serdes.String(), Serdes.Double())
            )
            .toStream()
            .map((k, v) -> new KeyValue<>("top_profit_book", v))
            .groupByKey(Grouped.with(Serdes.String(), Serdes.Double()))
            .reduce((v1, v2) -> v1 >= v2 ? v1 : v2)
            .toStream()
            .map((k, v) -> new KeyValue<>(k, totalMetricJson("top_profit_book", v)))
            .to("Results-top-profit-book", Produced.with(Serdes.String(), Serdes.String()));

        // ===== TIME-WINDOWED COMPUTATIONS — Last Hour =====

        // Req #14 — revenue last hour → time_window_metrics
        sales
            .map((k, v) -> new KeyValue<>("revenue_last_hour", v))
            .groupByKey(Grouped.with(Serdes.String(), saleSerde))
            .windowedBy(TimeWindows.of(Duration.ofHours(1)))
            .aggregate(
                () -> 0.0,
                (key, sale, aggr) -> aggr + (sale.price * sale.quantity),
                Materialized.with(Serdes.String(), Serdes.Double())
            )
            .toStream()
            .map((k, v) -> new KeyValue<>(k.key(), windowedMetricJson("revenue_last_hour", v)))
            .to("Results-revenue-last-hour", Produced.with(Serdes.String(), Serdes.String()));

        // Req #15 — expenses last hour → time_window_metrics
        purchases
            .map((k, v) -> new KeyValue<>("expenses_last_hour", v))
            .groupByKey(Grouped.with(Serdes.String(), purchaseSerde))
            .windowedBy(TimeWindows.of(Duration.ofHours(1)))
            .aggregate(
                () -> 0.0,
                (key, purchase, aggr) -> aggr + (purchase.cost * purchase.quantity),
                Materialized.with(Serdes.String(), Serdes.Double())
            )
            .toStream()
            .map((k, v) -> new KeyValue<>(k.key(), windowedMetricJson("expenses_last_hour", v)))
            .to("Results-expenses-last-hour", Produced.with(Serdes.String(), Serdes.String()));

        // ===== TOP COUNTRY SALES PER BOOK (Req #17) =====
        // Key: "book_id_country_id" (e.g. "1_3"), value: total revenue for that combo
        sales
            .map((k, v) -> new KeyValue<>(v.book_id + "_" + v.country_id, v))
            .groupByKey(Grouped.with(Serdes.String(), saleSerde))
            .aggregate(
                () -> 0.0,
                (key, sale, aggr) -> aggr + (sale.price * sale.quantity),
                Materialized.with(Serdes.String(), Serdes.Double())
            )
            .toStream()
            .map((k, v) -> new KeyValue<>(k, countryMetricJson(k, v)))
            .to("Results-top-country-sales-per-book", Produced.with(Serdes.String(), Serdes.String()));

        KafkaStreams streams = new KafkaStreams(builder.build(), properties);
        streams.cleanUp();
        streams.start();

        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));

        logger.info("Kafka Streams application started");
    }
}
