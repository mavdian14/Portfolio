import java.io.*;
import java.util.*;

public class Solution {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

    int b =  scanner.nextInt();
    int h = scanner.nextInt();
    scanner.close();

    try{
        if(b <= 0 || h <= 0){
        throw new Exception("Breadth and height must be positive");
    }
        System.out.println(b*h);

    }catch(Exception e){
        // toString() returns a string (can convert a string object into a string)
        System.out.println(e.toString());
    }
}
}
