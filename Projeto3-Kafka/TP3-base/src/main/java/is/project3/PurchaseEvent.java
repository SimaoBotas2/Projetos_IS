package is.project3;

import com.google.gson.JsonObject;

public class PurchaseEvent {
    public int book_id;
    public int supplier_id;
    public double cost;
    public int quantity;
    public long timestamp;

    public PurchaseEvent() {
    }

    public PurchaseEvent(int book_id, int supplier_id, double cost, int quantity, long timestamp) {
        this.book_id = book_id;
        this.supplier_id = supplier_id;
        this.cost = cost;
        this.quantity = quantity;
        this.timestamp = timestamp;
    }

    public JsonObject toJson() {
        JsonObject obj = new JsonObject();
        obj.addProperty("book_id", book_id);
        obj.addProperty("supplier_id", supplier_id);
        obj.addProperty("cost", cost);
        obj.addProperty("quantity", quantity);
        obj.addProperty("timestamp", timestamp);
        return obj;
    }

    public static PurchaseEvent fromJson(JsonObject json) {
        return new PurchaseEvent(
            json.get("book_id").getAsInt(),
            json.get("supplier_id").getAsInt(),
            json.get("cost").getAsDouble(),
            json.get("quantity").getAsInt(),
            json.get("timestamp").getAsLong()
        );
    }

    @Override
    public String toString() {
        return "PurchaseEvent{" +
                "book_id=" + book_id +
                ", supplier_id=" + supplier_id +
                ", cost=" + cost +
                ", quantity=" + quantity +
                ", timestamp=" + timestamp +
                '}';
    }
}
