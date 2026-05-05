package is.project3;

import com.google.gson.JsonObject;

public class SaleEvent {
    public int book_id;
    public int country_id;
    public double price;
    public int quantity;
    public long timestamp;

    public SaleEvent() {
    }

    public SaleEvent(int book_id, int country_id, double price, int quantity, long timestamp) {
        this.book_id = book_id;
        this.country_id = country_id;
        this.price = price;
        this.quantity = quantity;
        this.timestamp = timestamp;
    }

    public JsonObject toJson() {
        JsonObject obj = new JsonObject();
        obj.addProperty("book_id", book_id);
        obj.addProperty("country_id", country_id);
        obj.addProperty("price", price);
        obj.addProperty("quantity", quantity);
        obj.addProperty("timestamp", timestamp);
        return obj;
    }

    public static SaleEvent fromJson(JsonObject json) {
        return new SaleEvent(
            json.get("book_id").getAsInt(),
            json.get("country_id").getAsInt(),
            json.get("price").getAsDouble(),
            json.get("quantity").getAsInt(),
            json.get("timestamp").getAsLong()
        );
    }

    @Override
    public String toString() {
        return "SaleEvent{" +
                "book_id=" + book_id +
                ", country_id=" + country_id +
                ", price=" + price +
                ", quantity=" + quantity +
                ", timestamp=" + timestamp +
                '}';
    }
}
