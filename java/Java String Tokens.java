import java.io.*;
import java.util.*;

public class Solution {

    public static void main(String[] args) {
        Scanner scan = new Scanner(System.in);
        String s = scan.nextLine();
        // Write your code here.
        StringTokenizer arr = new StringTokenizer(s," !?_.,'@");
        // .countTokens() calculates the # of times that this Tokenizers nextToken() methods can be called before generating an exception
        System.out.println(arr.countTokens());
        //Returns: true if and only if there is at least one token in the string after the current position; false otherwise.
        
        while(arr.hasMoreTokens()){
            //Returns: the next token from this string tokenizer.
            System.out.println(arr.nextToken());
        }
        scan.close();
    }
}

