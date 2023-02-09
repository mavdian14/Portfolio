

import java.util.Comparator;
import java.util.stream.*;

class Student{
    int id;
    String name;
    double cgpa;
    
    public Student(int id, String name, double cgpa){
        this.id = id;
        this.name = name;
        this.cgpa = cgpa;
    }
    
    public int getID(){
        return id;
    }
    public String getName(){
        return name;
    }
    public double getCGPA(){
        return cgpa;
    }
}

class Priorities{
    public List<Student> getStudents(List<String> events){
        
        List<Student> studentlist = new ArrayList<Student>();
        
        for(String event : events){
            
            String[] temp = event.split(" ");
            
            if(temp[0].equals("ENTER")){
                
                Student student = new Student(Integer.parseInt(temp[3]),
                temp[1],
                Double.parseDouble(temp[2]));
                
                studentlist.add(student);
                
            }else if(temp[0].equals("SERVED")){
                if(!studentlist.isEmpty()){
                    //Returns a sequential Stream with this collection as its source.This method should be overridden when the spliterator() method cannot return a spliterator that is IMMUTABLE, CONCURRENT, or late-binding. (See spliterator() for details.)
                    studentlist = studentlist.stream().sorted(Comparator.comparing(Student::getCGPA)                                        .reversed().thenComparing(Student::getName)
                                    .thenComparing(Student::getID))
                                    .collect(Collectors.toList());
                    studentlist.remove(0);
                }
            }
        } 
        return studentlist;
    }
}
// .collect() is used to collect the stream elements to a collection

// .toList() returns a Collector that accumulates the input elements into a new List

// .comparing() accepts a function that extracts a Comparable sort key from a type T, and returns a Comparator<T> that compares by that sort key.The returned comparator is serializable if the specified function is also serializable.

// .thenComparing() returns a lexicographic-order comparator with another comparator. If this Comparator considers two elements equal, i.e. compare(a, b) == 0, other is used to determine the order.The returned comparator is serializable if the specified comparator is also serializable.
