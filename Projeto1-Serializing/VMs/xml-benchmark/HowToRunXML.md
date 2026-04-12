# Install Java & Maven
sudo apt update
sudo apt install openjdk-17-jdk maven -y

# Build
mvn clean package

# Run
java -cp target/xml-benchmark-1.0-SNAPSHOT.jar com.example.Main (deprecated)
java -jar target/xml-benchmark-1.0-SNAPSHOT.jar