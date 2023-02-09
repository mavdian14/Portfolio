import java.io.*;
import java.util.*;
import java.text.*;
import java.math.*;
import java.util.regex.*;

public class Solution {

    public static void main(String[] args) {
        Scanner get = new Scanner(System.in);
        int n = get.nextInt();
        int m = get.nextInt();
        
        BitSet b1 = new BitSet(n);
        BitSet b2 = new BitSet(n);
        // initializes a bitset array with 3 bitsets
        BitSet[] bitset = new BitSet[3];
        
        bitset[1]=b1;
        bitset[2]=b2;
        
        while(0<m--){
            String operation_name = get.next();
            int x = get.nextInt();
            int y = get.nextInt();
            
            if(operation_name.equals("AND")){
                // .and() returns b1 & b2 
                bitset[x].and(bitset[y]);
            }
            else if(operation_name.equals("OR")){
                // .or() returns the bitwise OR operation btwn b1 and b2
                bitset[x].or(bitset[y]);
            }
            // .flip() sets the bit at the specified index to the complement of its current value.
            else if(operation_name.equals("FLIP")){
                bitset[x].flip(y);
            }
            // Sets the bit at the specified index to true
            else if(operation_name.equals("SET")){
                bitset[x].set(y);
            }
            // .xor() returns the bitwise XOR opreation btwn x and y
            else if(operation_name.equals("XOR")){
                bitset[x].xor(bitset[y]);
            }
            // returns the num of bits set of b1+b2
            System.out.println(b1.cardinality()+" "+b2.cardinality());
        }
    }
}
 
