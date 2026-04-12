package com.example;

import jakarta.xml.bind.annotation.*;

@XmlAccessorType(XmlAccessType.FIELD)
public class Student {

    @XmlAttribute
    private String id;

    private String name;
    private int age;

    public Student() {}

    public Student(String id, String name, int age) {
        this.id = id;
        this.name = name;
        this.age = age;
    }
}