package is.project3;

import com.google.gson.JsonObject;

public class ResultEvent {
    public String metric_name;
    public String key;
    public double value;
    public long timestamp;

    public ResultEvent() {
    }

    public ResultEvent(String metric_name, String key, double value, long timestamp) {
        this.metric_name = metric_name;
        this.key = key;
        this.value = value;
        this.timestamp = timestamp;
    }

    public JsonObject toJson() {
        JsonObject obj = new JsonObject();
        obj.addProperty("metric_name", metric_name);
        obj.addProperty("key", key);
        obj.addProperty("value", value);
        obj.addProperty("timestamp", timestamp);
        return obj;
    }

    public static ResultEvent fromJson(JsonObject json) {
        return new ResultEvent(
            json.get("metric_name").getAsString(),
            json.get("key").getAsString(),
            json.get("value").getAsDouble(),
            json.get("timestamp").getAsLong()
        );
    }

    @Override
    public String toString() {
        return "ResultEvent{" +
                "metric_name='" + metric_name + '\'' +
                ", key='" + key + '\'' +
                ", value=" + value +
                ", timestamp=" + timestamp +
                '}';
    }
}
