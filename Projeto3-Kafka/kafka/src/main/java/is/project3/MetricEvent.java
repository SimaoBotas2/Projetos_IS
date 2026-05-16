package is.project3;

import com.google.gson.JsonObject;

/**
 * Generic metric event for analytics results.
 * Used for per-item metrics (revenue, expenses, profit, etc.)
 */
public class MetricEvent {
    public String key;
    public double value;
    public long timestamp;

    public MetricEvent() {
    }

    public MetricEvent(String key, double value, long timestamp) {
        this.key = key;
        this.value = value;
        this.timestamp = timestamp;
    }

    /**
     * Kept for internal Kafka Streams deserialization only.
     * JDBC Sink connectors no longer use this format directly —
     * they receive purpose-built schema+payload JSON from the helper methods
     * in ProjetoBase3Streams.
     */
    public JsonObject toJson() {
        JsonObject obj = new JsonObject();
        obj.addProperty("key", key);
        obj.addProperty("value", value);
        obj.addProperty("timestamp", timestamp);
        return obj;
    }

    public static MetricEvent fromJson(JsonObject json) {
        // Support both plain JSON and schema+payload envelope (from Connect)
        JsonObject data = json.has("payload") ? json.getAsJsonObject("payload") : json;
        return new MetricEvent(
            data.get("key").getAsString(),
            data.get("value").getAsDouble(),
            data.get("timestamp").getAsLong()
        );
    }

    @Override
    public String toString() {
        return "MetricEvent{" +
                "key='" + key + '\'' +
                ", value=" + value +
                ", timestamp=" + timestamp +
                '}';
    }
}
