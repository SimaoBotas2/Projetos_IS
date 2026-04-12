package com.example;

import com.fasterxml.jackson.annotation.JsonProperty;

public class RootWrapper {

    @JsonProperty("class")
    private ClassPackage classPackage;

    public RootWrapper() {}

    public RootWrapper(ClassPackage classPackage) {
        this.classPackage = classPackage;
    }

    public ClassPackage getClassPackage() {
        return classPackage;
    }

    public void setClassPackage(ClassPackage classPackage) {
        this.classPackage = classPackage;
    }
}