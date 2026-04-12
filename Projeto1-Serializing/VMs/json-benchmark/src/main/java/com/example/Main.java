package com.example;

import com.fasterxml.jackson.databind.ObjectMapper;

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
        RootWrapper root = new RootWrapper(classPackage);

        ObjectMapper mapper = new ObjectMapper();
        File file = new File("class.json");

        // -------- SERIALIZATION BENCHMARK --------
        long startSerialize = System.nanoTime();

        for (int i = 0; i < ITERATIONS; i++) {
            mapper.writeValue(file, root);
        }

        long endSerialize = System.nanoTime();
        long serializeTime = endSerialize - startSerialize;

        // -------- DESERIALIZATION BENCHMARK --------
        long startDeserialize = System.nanoTime();

        for (int i = 0; i < ITERATIONS; i++) {
            mapper.readValue(file, RootWrapper.class);
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