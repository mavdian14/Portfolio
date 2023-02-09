import java.io.*;
import java.util.*;
import java.text.*;
import java.math.*;
import java.util.regex.*;

public class Solution {

    public static void main(String[] args) {
        Scanner value = new Scanner(System.in);
        
        try
        {
            int x = value.nextInt();
            int y = value.nextInt();
            int result = x/y;
            System.out.println(result);
        }
        catch(InputMismatchException e){
            System.out.println("java.util.InputMismatchException");
        }
        catch(ArithmeticException e)
        {
            System.out.println("java.lang.ArithmeticException: " +e.getMessage());
        }
    }
}
