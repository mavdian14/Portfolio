import java.io.*;
import java.util.*;
import java.text.*;
import java.math.*;
import java.util.regex.*;

public class Solution {

    public static void main(String[] args) {
        Scanner scan = new Scanner(System.in);
        int i = 0;
        // hasNext() returns True if this scanner has another token in its input
        while (scan.hasNext()){
            ++i;
            // n denotes a whitespace character
            System.out.printf("%d %s %n", i , scan.nextLine());
        }
    }
}
