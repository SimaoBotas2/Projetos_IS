package is.project3;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import org.apache.kafka.common.serialization.Serializer;
import org.apache.kafka.common.serialization.Deserializer;

class PurchaseEventSerde {
    private static final Gson gson = new Gson();

    public static class PurchaseEventSerializer implements Serializer<PurchaseEvent> {
        @Override
        public byte[] serialize(String topic, PurchaseEvent data) {
            if (data == null) return null;
            return gson.toJson(data.toJson()).getBytes();
        }
    }

    public static class PurchaseEventDeserializer implements Deserializer<PurchaseEvent> {
        @Override
        public PurchaseEvent deserialize(String topic, byte[] data) {
            if (data == null) return null;
            JsonObject json = gson.fromJson(new String(data), JsonObject.class);
            return PurchaseEvent.fromJson(json);
        }
    }
}

class SaleEventSerde {
    private static final Gson gson = new Gson();

    public static class SaleEventSerializer implements Serializer<SaleEvent> {
        @Override
        public byte[] serialize(String topic, SaleEvent data) {
            if (data == null) return null;
            return gson.toJson(data.toJson()).getBytes();
        }
    }

    public static class SaleEventDeserializer implements Deserializer<SaleEvent> {
        @Override
        public SaleEvent deserialize(String topic, byte[] data) {
            if (data == null) return null;
            JsonObject json = gson.fromJson(new String(data), JsonObject.class);
            return SaleEvent.fromJson(json);
        }
    }
}

class ResultEventSerde {
    private static final Gson gson = new Gson();

    public static class ResultEventSerializer implements Serializer<ResultEvent> {
        @Override
        public byte[] serialize(String topic, ResultEvent data) {
            if (data == null) return null;
            return gson.toJson(data.toJson()).getBytes();
        }
    }

    public static class ResultEventDeserializer implements Deserializer<ResultEvent> {
        @Override
        public ResultEvent deserialize(String topic, byte[] data) {
            if (data == null) return null;
            JsonObject json = gson.fromJson(new String(data), JsonObject.class);
            return ResultEvent.fromJson(json);
        }
    }
}

class StringSerde {
    private static final Gson gson = new Gson();

    public static class StringSerializer implements Serializer<String> {
        @Override
        public byte[] serialize(String topic, String data) {
            if (data == null) return null;
            return data.getBytes();
        }
    }

    public static class StringDeserializer implements Deserializer<String> {
        @Override
        public String deserialize(String topic, byte[] data) {
            if (data == null) return null;
            return new String(data);
        }
    }
}
