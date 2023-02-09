import java.util.*;
import java.io.*;

class Solution{
    public static void main(String []argh){
        Scanner in = new Scanner(System.in);
        int t=in.nextInt();
        for(int i=0;i<t;i++){
            int a = in.nextInt();
            int b = in.nextInt();
            int n = in.nextInt();
            int total = 0;
            
            for(int j = 0; j < n; j++) {
                total += (Math.pow(2,j));
                //prints formatted output
                System.out.printf("%d ", a + total*b);
            }
            System.out.println();
        }
        in.close();
    }
}
