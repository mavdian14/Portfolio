import java.io.*;
import java.util.*;
import java.security.*;
public class Solution {

    public static void main(String[] args) throws NoSuchAlgorithmException {
        Scanner input = new Scanner(System.in);
        MessageDigest m = MessageDigest.getInstance("SHA-256");
        // .reset() resets the digest for further use
        m.reset();
        m.update(input.nextLine().getBytes());
        //Completes the hash computation by performing final operations such as padding. The digest is reset after this call is made. Returns:the array of bytes for the resulting hash value.
        for(byte i : m.digest()) {
            System.out.print(String.format("%02x", i));
        }
        System.out.println();
    }
}
