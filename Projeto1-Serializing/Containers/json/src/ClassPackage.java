import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class ClassPackage {

    @JsonProperty("student")
    private List<Student> student;

    public ClassPackage() {}

    public ClassPackage(List<Student> student) {
        this.student = student;
    }

    public List<Student> getStudent() { return student; }
    public void setStudent(List<Student> student) { this.student = student; }
}
