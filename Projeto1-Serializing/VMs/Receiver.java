import java.io.*;
import java.net.*;
import javax.xml.bind.*;

public class Receiver {

    private static final int PORT = 5000;

    public static void main(String[] args) throws Exception {

        ServerSocket serverSocket = new ServerSocket(PORT);
        System.out.println("Receiver waiting on port " + PORT);

        while (true) {
            Socket socket = serverSocket.accept();

            long startTime = System.nanoTime();

            InputStream in = socket.getInputStream();
            ByteArrayOutputStream buffer = new ByteArrayOutputStream();

            byte[] data = new byte[4096];
            int bytesRead;
            while ((bytesRead = in.read(data)) != -1) {
                buffer.write(data, 0, bytesRead);
            }

            long endTime = System.nanoTime();

            byte[] xmlBytes = buffer.toByteArray();

            // Deserialize
            JAXBContext context = JAXBContext.newInstance(ClassPackage.class);
            Unmarshaller unmarshaller = context.createUnmarshaller();
            ClassPackage classPackage = (ClassPackage)
                    unmarshaller.unmarshal(new ByteArrayInputStream(xmlBytes));

            long durationNs = endTime - startTime;
            double durationSec = durationNs / 1_000_000_000.0;
            double throughput = xmlBytes.length / durationSec;

            System.out.println("Received bytes: " + xmlBytes.length);
            System.out.println("Time (sec): " + durationSec);
            System.out.println("Throughput (bytes/sec): " + throughput);
            System.out.println("Students received: " + classPackage.getStudents().size());

            socket.close();
        }
    }
}