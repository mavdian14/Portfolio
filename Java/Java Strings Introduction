import java.io.*;
import java.util.*;

public class Solution {

    public static void main(String[] args) {
        
        Scanner sc=new Scanner(System.in);
        // finds & returns the next complete token in this scanner
        String A=sc.next();
    String B=sc.next();
    //Sum of the lengths
    System.out.println(A.length()+B.length());

    //.compareTo() compares 2 str's lexographically
    int result = A.compareTo(B);
    if(result<0 || result ==0){
        System.out.println("No");
    }else{
        System.out.println("Yes");
    }

    //Capitalize and print together

    // toUpperCase() converts all chars in str to UpperCase (similar for toLowerCase() )
    A= A.substring(0,1).toUpperCase()+A.substring(1).toLowerCase();
    B= B.substring(0, 1).toUpperCase()+B.substring(1).toLowerCase();

    System.out.println(A+" "+B);
    }
}



