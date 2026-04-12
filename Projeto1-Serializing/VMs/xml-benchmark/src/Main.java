package com.example;

import jakarta.xml.bind.*;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class Main {

    private static final int ITERATIONS = 10000;

    public static void main(String[] args) throws Exception {

        List<Student> students = new ArrayList<>();
        students.add(new Student("201134441110", "Alberto", 21));
        students.add(new Student("201134441116", "Patricia", 21));
        students.add(new Student("201134441210", "Luis", 21));

        ClassPackage classPackage = new ClassPackage(students);

        JAXBContext context = JAXBContext.newInstance(ClassPackage.class);
        Marshaller marshaller = context.createMarshaller();
        Unmarshaller unmarshaller = context.createUnmarshaller();

        File file = new File("class.xml");

        // -------- SERIALIZATION BENCHMARK --------
        long startSerialize = System.nanoTime();

        for (int i = 0; i < ITERATIONS; i++) {
            marshaller.marshal(classPackage, file);
        }

        long endSerialize = System.nanoTime();
        long serializeTime = endSerialize - startSerialize;

        // -------- DESERIALIZATION BENCHMARK --------
        long startDeserialize = System.nanoTime();

        for (int i = 0; i < ITERATIONS; i++) {
            unmarshaller.unmarshal(file);
        }

        long endDeserialize = System.nanoTime();
        long deserializeTime = endDeserialize - startDeserialize;

        printMetrics("Serialization", serializeTime);
        printMetrics("Deserialization", deserializeTime);
    }

    private static void printMetrics(String operation, long timeNano) {
        double timeSeconds = timeNano / 1_000_000_000.0;
        double throughput = ITERATIONS / timeSeconds;

        Runtime runtime = Runtime.getRuntime();
        runtime.gc();
        long memoryUsed = (runtime.totalMemory() - runtime.freeMemory()) / (1024 * 1024);

        System.out.println("==== " + operation + " ====");
        System.out.println("Time (seconds): " + timeSeconds);
        System.out.println("Throughput (ops/sec): " + throughput);
        System.out.println("Memory Used (MB): " + memoryUsed);
        System.out.println();
    }
}