# Java Version
sudo apt install openjdk-17-jdk
# Dependencies
sudo apt install libjaxb-api-java libjaxb-java
# Compile java files
javac *.java
javac -cp .:/usr/share/java/jaxb-api.jar:/usr/share/java/jaxb-impl.jar:/usr/share/java/jaxb-core.jar *.java
# Run file
java Sender
java -cp .:/usr/share/java/jaxb-api.jar:/usr/share/java/jaxb-impl.jar:/usr/share/java/jaxb-core.jar Receiver
# Arquitecture
VM1 (Sender)  ───── LAN ─────►  VM2 (Receiver)
Serialize XML                Deserialize XML
Measure send time            Measure receive time
Calculate throughput         Log metrics
# Metrics
| Metric                 | Description      |
| ---------------------- | ---------------- |
| Packet size (bytes)    | Size of XML      |
| Send time (sec)        | Time to transmit |
| Receive time (sec)     | Time to receive  |
| Throughput (bytes/sec) | Bytes / second   |
| CPU usage              | `top`            |
| Memory usage           | `free -m`        |
| Network speed          | `iperf3` test    |
# Network speed
sudo apt install iperf3
iperf3 -s => VM2
iperf3 -c 192.168.1.101 => VM1
# Larger XML
for(int i = 0; i < 10000; i++) {
    students.add(new Student("ID"+i, "Name"+i, 20));
}
# Create CSV Output
FileWriter writer = new FileWriter("results.csv", true);
writer.write(xmlBytes.length + "," + durationSec + "," + throughput + "\n");
writer.close();