FROM eclipse-temurin:8-jdk-jammy

WORKDIR /app

COPY src/*.java ./
RUN javac *.java

EXPOSE 5000

CMD ["java", "Receiver"]
