import javax.xml.bind.annotation.*;
import java.util.List;

@XmlRootElement(name = "class", namespace = "http://www.dei.uc.pt/EAI")
@XmlAccessorType(XmlAccessType.FIELD)
public class ClassPackage {

    @XmlElement(name = "student")
    private List<Student> students;

    public ClassPackage() {}

    public ClassPackage(List<Student> students) {
        this.students = students;
    }

    public List<Student> getStudents() {
        return students;
    }
}
