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

    public JsonObject toJson() {
        JsonObject obj = new JsonObject();
        obj.addProperty("key", key);
        obj.addProperty("value", value);
        obj.addProperty("timestamp", timestamp);
        return obj;
    }

    public static MetricEvent fromJson(JsonObject json) {
        return new MetricEvent(
            json.get("key").getAsString(),
            json.get("value").getAsDouble(),
            json.get("timestamp").getAsLong()
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
