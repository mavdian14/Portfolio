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

public class Solution {

  static class Node {
    int x;
    long code;
    public Node(int x, long code) {
      this.x = x;
      this.code = code;
    }
  }
  
  public static int[][] build(int[] a) {
    int n = a.length;
    int b = 32 - Integer.numberOfLeadingZeros(n);
    int[][] ret = new int[b][];
    for (int i = 0, l = 1; i < b; i++, l *= 2) {
      if (i == 0) {
        ret[i] = a;
      } else {
        ret[i] = new int[n - l + 1];
        for (int j = 0; j < n - l + 1; j++) {
          ret[i][j] = Math.min(ret[i - 1][j], ret[i - 1][j + l / 2]);
        }
      }
    }
    return ret;
  }

  public static int rmq(int[][] or, int l, int r) {
    assert l <= r;
    if (l >= r)
      return Integer.MAX_VALUE;
    int t = 31 - Integer.numberOfLeadingZeros(r - l);
    return Math.min(or[t][l], or[t][r - (1 << t)]);
  }

  public static void main(String[] args) throws IOException {
    BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
    BufferedWriter bw = new BufferedWriter(new FileWriter(System.getenv("OUTPUT_PATH")));

    StringTokenizer st = new StringTokenizer(br.readLine());
    int n = Integer.parseInt(st.nextToken());
    int k = Integer.parseInt(st.nextToken());

    int[] a = new int[n];
    int[] ra = new int[n];
    st = new StringTokenizer(br.readLine());
    for (int i = 0; i < n; i++) {
      int item = Integer.parseInt(st.nextToken());
      a[i] = item;
      ra[i] = -a[i];
    }

    int[][] stmin = build(a);
    int[][] stmax = build(ra);

    Node[] efs = new Node[80 * n];
    int efp = 0;

    int[][] oas = new int[0][];
    for (int i = n - 1; i >= 0; i--) {
      int[][] noas = new int[40][];
      int p = 0;
      for (int j = 0; j < oas.length; j++) {
        oas[j][0] |= a[i];
        oas[j][1] &= a[i];
        if (p > 0 && noas[p - 1][0] == oas[j][0] && noas[p - 1][1] == oas[j][1]) {
          noas[p - 1][2] = oas[j][2];
        } else {
          noas[p++] = oas[j];
        }
      }
      if (!(p > 0 && noas[p - 1][0] == a[i] && noas[p - 1][1] == a[i])) {
        noas[p++] = new int[] { a[i], a[i], i };
      } else {
        noas[p - 1][2] = i;
      }
      oas = Arrays.copyOf(noas, p);

      int to = n;
      for (int[] oa : oas) {
        int cha = oa[0] - oa[1];
        int low = oa[2] - 1, high = to;
        while (high - low > 1) {
          int h = high + low >> 1;
          if (cha - (-rmq(stmax, i, h + 1) - rmq(stmin, i, h + 1)) >= k) {
            low = h;
          } else {
            high = h;
          }
        }
        if (low >= oa[2]) {
          efs[efp++] = new Node(i, (long) (low - i + 1) << 32 | i);
          efs[efp++] = new Node(low + 1, (long) (low - i + 1) << 32 | i);
        }
        to = oa[2];
      }
    }

    Arrays.sort(efs, 0, efp, (efsa, efsb) -> { return efsa.x - efsb.x;  });

    TreeSet<Long> set = new TreeSet<>();

    int q = 0;
    for (int i = 0; i < n; i++) {
      int result = -1;
      while (q < efp && efs[q].x <= i) {
        long code = efs[q].code;
        if (set.contains(code)) {
          set.remove(code);
        } else {
          set.add(code);
        }
        q++;
      }
      if (!set.isEmpty()) {
        result = Math.max(result, (int) (set.last() >>> 32));
      }
      bw.write(result + "\n");
    }

    bw.newLine();
    bw.close();
    br.close();
  }
}
