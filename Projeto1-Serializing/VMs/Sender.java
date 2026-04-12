import java.io.*;
import java.net.*;
import java.util.*;
import javax.xml.bind.*;

public class Sender {

    private static final String HOST = "192.168.1.101";
    private static final int PORT = 5000;

    public static void main(String[] args) throws Exception {

        List<Student> students = new ArrayList<>();
        students.add(new Student("201134441110", "Alberto", 21));
        students.add(new Student("201134441116", "Patricia", 21));
        students.add(new Student("201134441210", "Luis", 21));

        ClassPackage classPackage = new ClassPackage(students);

        JAXBContext context = JAXBContext.newInstance(ClassPackage.class);
        Marshaller marshaller = context.createMarshaller();
        marshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, true);

        ByteArrayOutputStream out = new ByteArrayOutputStream();
        marshaller.marshal(classPackage, out);

        byte[] xmlBytes = out.toByteArray();

        Socket socket = new Socket(HOST, PORT);

        long startTime = System.nanoTime();

        OutputStream socketOut = socket.getOutputStream();
        socketOut.write(xmlBytes);
        socketOut.flush();
        socket.shutdownOutput();

        long endTime = System.nanoTime();

        double durationSec = (endTime - startTime) / 1_000_000_000.0;
        double throughput = xmlBytes.length / durationSec;

        System.out.println("Sent bytes: " + xmlBytes.length);
        System.out.println("Send time (sec): " + durationSec);
        System.out.println("Send throughput (bytes/sec): " + throughput);

        socket.close();
    }
}