package is.project3;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Properties;
import java.util.Random;

public class PurchaseEventProducer {
    private static final Logger logger = LoggerFactory.getLogger(PurchaseEventProducer.class);
    private static final Random random = new Random();
    private static final Gson gson = new Gson();

    private static final int[] BOOK_IDS = {1, 2, 3, 4, 5};
    private static final int[] SUPPLIER_IDS = {1, 2, 3, 4, 5};
    private static final double[] BOOK_COSTS = {500.0, 15.0, 40.0, 150.0, 2.0};

    public static void main(String[] args) {
        Properties properties = new Properties();
        properties.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "broker1:9092,broker2:9092");
        properties.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        properties.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        properties.put(ProducerConfig.ACKS_CONFIG, "all");

        try (KafkaProducer<String, String> producer = new KafkaProducer<>(properties)) {
            logger.info("Starting Purchase Event Producer");
            
            for (int i = 0; i < 1000; i++) {
                PurchaseEvent event = generatePurchaseEvent();
                String key = "purchase_" + i;
                String value = gson.toJson(event.toJson());

                ProducerRecord<String, String> record = new ProducerRecord<>("Purchases", key, value);
                producer.send(record, (metadata, exception) -> {
                    if (exception != null) {
                        logger.error("Error sending purchase event", exception);
                    } else {
                        logger.info("Sent purchase event: {}", event);
                    }
                });

                Thread.sleep(100); // Simulate events coming over time
            }

            producer.flush();
            logger.info("Purchase Event Producer finished");
        } catch (Exception e) {
            logger.error("Producer error", e);
        }
    }

    private static PurchaseEvent generatePurchaseEvent() {
        int bookId = BOOK_IDS[random.nextInt(BOOK_IDS.length)];
        int supplierId = SUPPLIER_IDS[random.nextInt(SUPPLIER_IDS.length)];
        double cost = BOOK_COSTS[bookId - 1] * (0.8 + 0.4 * random.nextDouble()); // ±20% variation
        int quantity = 1 + random.nextInt(20);
        long timestamp = System.currentTimeMillis();

        return new PurchaseEvent(bookId, supplierId, cost, quantity, timestamp);
    }
}
