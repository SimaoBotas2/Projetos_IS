package com.example;

import jakarta.xml.bind.annotation.*;
import java.util.List;

@XmlRootElement(name = "class", namespace = "http://www.dei.uc.pt/EAI")
@XmlAccessorType(XmlAccessType.FIELD)
public class ClassPackage {

    @XmlElement(name = "student")
    private List<Student> student;

    public ClassPackage() {}

    public ClassPackage(List<Student> student) {
        this.student = student;
    }
}