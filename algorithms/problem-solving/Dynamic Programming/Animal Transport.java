import java.io.*;
import java.math.*;
import java.security.*;
import java.text.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.regex.*;

public class Solution {

  static class LazySegment {
    int n;
    int h;
    int[] a;
    int[] f;

    public LazySegment(int n) {
      this.n = n;
      //Returns the number of zero bits preceding the highest-order ("leftmost") one-bit in the two's complement binary representation of the specified int value.
      h = 32 - Integer.numberOfLeadingZeros(n);
      int base = (1 << h);
      a = new int[base << 1];
      f = new int[base << 1];
    }

    void rangeApply(int l, int r, int z) {
      rangeApply(0, 0, n, l, r, z);
    }

    void rangeApply(int i, int il, int ir, int l, int r, int z) {
      if (l <= il && ir <= r) {
        a[i] = z + a[i];
        if (i < f.length) {
          f[i] = z + f[i];
        }
      } else if (ir <= l || r <= il) {

      } else {
        rangeApply(2 * i + 1, il, (il + ir) / 2, 0, n, f[i]);
        rangeApply(2 * i + 2, (il + ir) / 2, ir, 0, n, f[i]);
        f[i] = 0;
        rangeApply(2 * i + 1, il, (il + ir) / 2, l, r, z);
        rangeApply(2 * i + 2, (il + ir) / 2, ir, l, r, z);
        a[i] = Math.max(a[2 * i + 1], a[2 * i + 2]);
      }
    }

    int rangeConcat(int l, int r) {
      return rangeConcat(0, 0, n, l, r);
    }

    int rangeConcat(int i, int il, int ir, int l, int r) {
      if (l <= il && ir <= r) {
        return a[i];
      } else if (ir <= l || r <= il) {
        return 0;
      } else {
        return f[i]
            + Math.max(
                rangeConcat(2 * i + 1, il, (il + ir) / 2, l, r),
                rangeConcat(2 * i + 2, (il + ir) / 2, ir, l, r));
      }
    }
  }

  public static void main(String[] args) throws IOException {
    BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
    BufferedWriter bw = new BufferedWriter(new FileWriter(System.getenv("OUTPUT_PATH")));

    StringTokenizer st = new StringTokenizer(br.readLine());
    int cases = Integer.parseInt(st.nextToken());

    for (int itr = 0; itr < cases; itr++) {
      st = new StringTokenizer(br.readLine());
      int m = Integer.parseInt(st.nextToken());
      int n = Integer.parseInt(st.nextToken());

      char[] t = new char[n];
      st = new StringTokenizer(br.readLine());
      for (int i = 0; i < n; i++) {
        char item = st.nextToken().charAt(0);
        t[i] = item;
      }

      int[] s = new int[n];
      st = new StringTokenizer(br.readLine());
      for (int i = 0; i < n; i++) {
        int item = Integer.parseInt(st.nextToken());
        s[i] = item - 1;
      }

      int[] d = new int[n];
      st = new StringTokenizer(br.readLine());
      for (int i = 0; i < n; i++) {
        int item = Integer.parseInt(st.nextToken());
        d[i] = item - 1;
      }
      @SuppressWarnings("unchecked")
      List<Integer>[] fromD = new List[m];
      for (int i = 0; i < n; i++) {
        if (s[i] < d[i]) {
          if (fromD[d[i]] == null) {
            fromD[d[i]] = new ArrayList<>();
          }
          fromD[d[i]].add(i);
        }
      }

      LazySegment segtree0 = new LazySegment(m + 1);
      LazySegment segtree1 = new LazySegment(m + 1);
      int[] dp = new int[m];
      for (int x = 0; x < m; x++) {
        if (fromD[x] != null) {
          for (int i : fromD[x]) {
            if (t[i] == 'E' || t[i] == 'C') {
              segtree0.rangeApply(0, s[i] + 1, 1);
            } else {
              segtree1.rangeApply(0, s[i] + 1, 1);
            }
          }
        }
        dp[x] = Math.max(segtree0.rangeConcat(0, x + 1), segtree1.rangeConcat(0, x + 1));
        segtree0.rangeApply(x, x + 1, dp[x]);
        segtree1.rangeApply(x, x + 1, dp[x]);
      }

      int y = 1;
      for (int x = 0; ; y++) {
        while (x < m && dp[x] < y) {
          x++;
        }
        if (x == m) {
          break;
        }
        bw.write((x + 1) + " ");
      }
      for (; y <= n; y++) {
        bw.write(y < n ? "-1 " : "-1");
      }

      bw.newLine();
    }

    bw.close();
    br.close();
  }
}
