import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.util.ArrayList;
import java.util.List;

public class Main {

    private static final int ITERATIONS = 1;

    public static void main(String[] args) throws Exception {

        int recordCount = args.length >= 1 ? Integer.parseInt(args[0])
                : Integer.parseInt(System.getenv().getOrDefault("RECORD_COUNT", "10000"));

        List<Student> students = new ArrayList<>();

        for(int i = 0; i < recordCount; i++){
            students.add(new Student("2011344412" + i, "Student" + i, 21));
        }

        ClassPackage classPackage = new ClassPackage(students);
        RootWrapper root = new RootWrapper(classPackage);

        ObjectMapper mapper = new ObjectMapper();

        // Warm-up: Jackson JIT compilation
        ByteArrayOutputStream warmupBuffer = new ByteArrayOutputStream();
        mapper.writeValue(warmupBuffer, root);

        // -------- SERIALIZATION BENCHMARK --------
        long startSerialize = System.nanoTime();

        ByteArrayOutputStream buffer = new ByteArrayOutputStream();
        for (int i = 0; i < ITERATIONS; i++) {
            buffer.reset();
            mapper.writeValue(buffer, root);
        }

        long endSerialize = System.nanoTime();
        long serializeTime = endSerialize - startSerialize;
        byte[] data = buffer.toByteArray();

        // -------- DESERIALIZATION BENCHMARK --------
        long startDeserialize = System.nanoTime();

        for (int i = 0; i < ITERATIONS; i++) {
            mapper.readValue(new ByteArrayInputStream(data), RootWrapper.class);
        }

        long endDeserialize = System.nanoTime();
        long deserializeTime = endDeserialize - startDeserialize;

        printMetrics("Serialization", serializeTime, data);
        printMetrics("Deserialization", deserializeTime, data);
    }

    private static void printMetrics(String operation, long timeNano, byte[] data) {
        long bytes = data.length;
        double timeSeconds = timeNano / 1_000_000_000.0;
        double throughput = bytes / timeSeconds;

        Runtime runtime = Runtime.getRuntime();
        runtime.gc();
        long memoryUsed = (runtime.totalMemory() - runtime.freeMemory()) / (1024 * 1024);

        System.out.println("==== " + operation + " ====");
        System.out.println("Size (bytes): " + bytes);
        System.out.println("Time (seconds): " + timeSeconds);
        System.out.println("Throughput (bytes/sec): " + throughput);
        System.out.println("Memory Used (MB): " + memoryUsed);
        System.out.println();
    }
}