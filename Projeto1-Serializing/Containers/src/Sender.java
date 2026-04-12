import java.io.*;
import java.util.*;
import javax.xml.bind.*;

public class Sender {

    private static final int ITERATIONS = 1;

    public static void main(String[] args) throws Exception {

        int recordCount = args.length >= 1 ? Integer.parseInt(args[0])
                : Integer.parseInt(System.getenv().getOrDefault("RECORD_COUNT", "10000"));

        List<Student> students = new ArrayList<>();

        for(int i = 0; i < recordCount; i++){
            students.add(new Student("2011344412"+i, "Student"+i, 21));
        }
        ClassPackage classPackage = new ClassPackage(students);

        JAXBContext context = JAXBContext.newInstance(ClassPackage.class);
        Marshaller marshaller = context.createMarshaller();
        marshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, true);
        Unmarshaller unmarshaller = context.createUnmarshaller();

        // Warm-up: JAXB JIT compilation
        ByteArrayOutputStream warmupOut = new ByteArrayOutputStream();
        marshaller.marshal(classPackage, warmupOut);

        // -------- SERIALIZATION BENCHMARK --------
        long startSerialize = System.nanoTime();

        ByteArrayOutputStream out = new ByteArrayOutputStream();
        for (int i = 0; i < ITERATIONS; i++) {
            out.reset();
            marshaller.marshal(classPackage, out);
        }

        long endSerialize = System.nanoTime();
        long serializeTime = endSerialize - startSerialize;

        byte[] xmlBytes = out.toByteArray();

        // -------- DESERIALIZATION BENCHMARK --------
        long startDeserialize = System.nanoTime();

        for (int i = 0; i < ITERATIONS; i++) {
            unmarshaller.unmarshal(new ByteArrayInputStream(xmlBytes));
        }

        long endDeserialize = System.nanoTime();
        long deserializeTime = endDeserialize - startDeserialize;

        printMetrics("Serialization", serializeTime, xmlBytes);
        printMetrics("Deserialization", deserializeTime, xmlBytes);
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
