import java.util.*;
import java.text.*;

public class Solution {
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        double payment = scanner.nextDouble();
        scanner.close();
        
        //getCurrencyInstance() returns the currency instance of a specified locale. .format() returns a formatted string
        String us = NumberFormat.getCurrencyInstance(Locale.US).format(payment);
// .substring() returns a substring of str i.e. substring(1) is equivalent to str[1:]    
String india = "Rs." + us.substring(1);
String china = NumberFormat.getCurrencyInstance(Locale.CHINA).format(payment);
String france = NumberFormat.getCurrencyInstance(Locale.FRANCE).format(payment); 
        
        System.out.println("US: " + us);
        System.out.println("India: " + india);
        System.out.println("China: " + china);
        System.out.println("France: " + france);
    }
}
