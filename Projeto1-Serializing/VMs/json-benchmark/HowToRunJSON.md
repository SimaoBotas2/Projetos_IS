# Install Java & Maven
sudo apt update
sudo apt install openjdk-17-jdk maven -y

# Build
mvn clean package

# Run
java -jar target/json-benchmark-1.0-SNAPSHOT.jar

# Why Wrapper
because JSON root has "class"