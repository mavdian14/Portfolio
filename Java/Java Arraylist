import java.io.*;
import java.util.*;
import java.text.*;
import java.math.*;
import java.util.regex.*;

public class Solution {

    public static void main(String[] args) throws Exception {
        Scanner scanner = new Scanner(System.in);
        ArrayList<ArrayList<Integer>> arrayList = new ArrayList<>();
        ArrayList<Integer> temp = new ArrayList<>();

        int n = scanner.nextInt();
        int m = 0;
        for (int i = 0; i < n; i++) {
            m = scanner.nextInt();
            for (int j = 0; j < m; j++) {
                temp.add(scanner.nextInt());
            }
            // .clone(): Returns a shallow copy of this ArrayList instance. (The elements themselves are not copied.)
            arrayList.add((ArrayList<Integer>) temp.clone());
            // .clear(): Removes all of the elements from this list. The list will be empty after this call returns.
            temp.clear();
        }
        int q = scanner.nextInt();
        for (int i = 0; i < q; i++) {
            try {
                System.out.println(arrayList.get(scanner.nextInt() - 1).get(scanner.nextInt() - 1));
            } catch (Exception e) {
                System.out.println("ERROR!");
            }
        }


//        for (ArrayList<Integer> i : arrayList) {
//            i.forEach(el -> System.out.print(" " + el));
//            System.out.println();
//        }
    }

}
