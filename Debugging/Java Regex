import java.io.*;
import java.util.*;
import java.util.regex.Matcher;
import java.util.Scanner;
import java.util.regex.Pattern;

public class Solution {

    public static void main(String[] args){
        Scanner in = new Scanner(System.in);
        // hasNext() returns true if scanner has another scanner token in its output
        while(in.hasNext()){
            String IP = in.next();
            // .matches() returns whether given string matches the given regex
            System.out.println(IP.matches(new MyRegex().pattern));
        }
        }
    }
class MyRegex{
    static String pattern = "^(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$";
}
