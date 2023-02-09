import java.io.*;
import java.math.*;
import java.security.*;
import java.text.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.regex.*;

public class Solution {

  static long square(long x) {
    return x * x; 
  }
  static long[] dp;
  static int[] criminals;

  static long distance(int x, int y) {
    return (square(criminals[y]) - square(criminals[x]) + dp[y] - dp[x]);
  }
  
  static long policeOperation(int n, int h, int[] criminals) {
    dp = new long[n + 1];
    int[] q = new int[n + 1];
    int fr = 0;
    int re = 1;
    for (int i = 1; i <= n; i++) {
      while (fr + 1 < re 
          && 2 * (long)criminals[i-1] * (criminals[q[fr + 1]] - criminals[q[fr]]) > distance(q[fr], q[fr + 1])) {
        fr++;
      }
      dp[i] = dp[q[fr]] + square(criminals[i-1] - criminals[q[fr]]) + h;
      if (i < n) {
        while (fr <= re - 2 
            && distance(q[re - 2], q[re - 1]) / (criminals[q[re - 1]] - criminals[q[re - 2]]) >
        distance(q[re - 1], i) / (criminals[i] - criminals[q[re - 1]])) {
          re--;
        }
        q[re] = i;
        re++;
      }
    }
    return dp[n];
  }

  public static void main(String[] args) throws IOException {
    BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
    BufferedWriter bw = new BufferedWriter(new FileWriter(System.getenv("OUTPUT_PATH")));

    StringTokenizer st = new StringTokenizer(br.readLine());
    int n = Integer.parseInt(st.nextToken());
    int h = Integer.parseInt(st.nextToken());

    long result = 0;
    if (h > 0 && n > 0) {
      criminals = new int[n];
      int index = 0;

      st = new StringTokenizer(br.readLine());
      for (int i = 0; i < n; i++) {
        int item = Integer.parseInt(st.nextToken());
        if (index == 0 || item > criminals[index]) {
          criminals[index++] = item;
        }
      }
      result = policeOperation(index, h, criminals);
    }

    bw.write(String.valueOf(result));
    bw.newLine();

    br.close();
    bw.close();
  }
}
