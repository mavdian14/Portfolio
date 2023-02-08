import java.io.*;
import java.math.*;
import java.security.*;
import java.text.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;
import java.util.regex.*;
import java.util.stream.*;
import static java.util.stream.Collectors.joining;
import static java.util.stream.Collectors.toList;
import java.util.Scanner;

public class HackerRankCandleCountingFenwick {
   private static final Scanner scanner = new Scanner(System.in);

   private static final long PLONG = (long) Math.pow(10, 9) + 7;
   private static final int PINT = (int) Math.pow(10, 9) + 7;

   public static class FenwickCandles {
      private final int[] array;

      public FenwickCandles(int size) {
         array = new int[size + 1];
      }

      public int treeSum() {
         return sumUpToIdx(this.size() - 1);
      }

      public int sumUpToIdx(int idx) {
         idx++;  // translate from 0-indexed input to 1-indexed array
         assert idx > 0;
         long sum = 0;
         while (idx > 0) {
            sum += array[idx];
            idx -= idx & (-idx);
         }
         return (int) (sum % PLONG);
      }

      public void update(int idx, int value) {
         idx++;  // translate from 0-indexed input to 1-indexed array
         assert idx > 0;
         while (idx < array.length) {
            array[idx] = (array[idx] + value) % PINT;
            idx += idx & (-idx);
         }
      }

      public int size() {
         return array.length - 1;
      }
   }

   static int candlesCounting(int k, int n, int[][] candles, int maxHeight) {

      int bLen = (int) Math.pow(2, k);
      FenwickCandles[] allBSTs = new FenwickCandles[bLen];
      int[] newCount = new int[bLen];

      for (int tree = 1; tree < bLen; tree++) {
         allBSTs[tree] = new FenwickCandles(maxHeight + 1);
      }

      for (int i = 0; i < n; i++) {
         int height = candles[i][0];
         int candleColor = candles[i][1] - 1;
         newCount[1 << candleColor] = 1;
         for (int tree = 1; tree < bLen; tree++) {
            int count = allBSTs[tree].sumUpToIdx(height - 1);
            if (count > 0) {
               // nth bit represents color n
               int newJ = tree | (1 << candleColor);
               newCount[newJ] = (newCount[newJ] + count) % PINT;
            }
            if (newCount[tree] > 0) {
               allBSTs[tree].update(height, newCount[tree]);
               newCount[tree] = 0;
            }
         }
      }
      return allBSTs[bLen - 1].treeSum();
   }
    

   public static void main(String[] args) {
      String[] nk = scanner.nextLine().split(" ");
      int n = Integer.parseInt(nk[0]);
      int k = Integer.parseInt(nk[1]);
      int[][] candles = new int[n][2];
      int maxH = 0;
      for (int row = 0; row < n; row++) {
         String[] s = scanner.nextLine().split(" ");
         for (int col = 0; col < 2; col++) {
            int i = Integer.parseInt(s[col]);
            if (col == 0 && i > maxH) {
               maxH = i;
            }
            candles[row][col] = i;
         }
      }
      int result = candlesCounting(k, n, candles, maxH);
      System.out.println(result);
      scanner.close();
   }
}
