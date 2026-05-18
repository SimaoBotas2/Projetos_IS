package is.project3;

import com.google.gson.Gson;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Properties;
import java.util.Random;

public class SaleEventProducer {
    private static final Logger logger = LoggerFactory.getLogger(SaleEventProducer.class);
    private static final Random random = new Random();
    private static final Gson gson = new Gson();

    private static final int[] BOOK_IDS = {1, 2, 3, 4, 5};
    private static final int[] COUNTRY_IDS = {1, 2, 3, 4, 5};
    private static final double[] BOOK_PRICES = {899.99, 29.99, 79.99, 299.99, 9.99};

    public static void main(String[] args) {
        Properties properties = new Properties();
        properties.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "broker1:9092,broker2:9092,broker3:9092");
        properties.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        properties.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        properties.put(ProducerConfig.ACKS_CONFIG, "all");

        try (KafkaProducer<String, String> producer = new KafkaProducer<>(properties)) {
            logger.info("Starting Sale Event Producer");
            
            for (int i = 0; i < 1500; i++) {
                SaleEvent event = generateSaleEvent();
                String key = "sale_" + i;
                String value = gson.toJson(event.toJson());

                ProducerRecord<String, String> record = new ProducerRecord<>("Sales", key, value);
                producer.send(record, (metadata, exception) -> {
                    if (exception != null) {
                        logger.error("Error sending sale event", exception);
                    } else {
                        logger.info("Sent sale event: {}", event);
                    }
                });

                Thread.sleep(50); // Sales happen more frequently than purchases
            }

            producer.flush();
            logger.info("Sale Event Producer finished");
        } catch (Exception e) {
            logger.error("Producer error", e);
        }
    }

    private static SaleEvent generateSaleEvent() {
        int bookId = BOOK_IDS[random.nextInt(BOOK_IDS.length)];
        int countryId = COUNTRY_IDS[random.nextInt(COUNTRY_IDS.length)];
        double price = BOOK_PRICES[bookId - 1] * (0.9 + 0.2 * random.nextDouble()); // ±10% variation
        int quantity = 1 + random.nextInt(10);
        long timestamp = System.currentTimeMillis();

        return new SaleEvent(bookId, countryId, price, quantity, timestamp);
    }
}
