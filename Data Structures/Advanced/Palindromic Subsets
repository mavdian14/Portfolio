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
    public static final long MOD = 1_000_000_007;
  public static final int MAX = 26;

  static int[] temp = new int[MAX];
  
  static class Frequency {
      int[] freq = new int[MAX];

      public Frequency() {
    }
      
      public Frequency(int c) {
          freq[c]++;
    }

      public Frequency(Frequency a, Frequency b) {
        for (int i = 0; i < a.freq.length; i++) {
            freq[i] = a.freq[i] + b.freq[i];
        }
    }
      
    void shift(int x) {
          System.arraycopy(freq, 0, temp, 0, freq.length);
          for (int i = 0; i < freq.length; i++) {
              freq[(i + x) % MAX] = temp[i];
          }
      }
    
    void sum(Frequency a) {
          for (int i = 0; i < freq.length; i++) {
              freq[i] += a.freq[i];
          }
    }
    
    void sum(Frequency a, Frequency b) {
        for (int i = 0; i < a.freq.length; i++) {
            freq[i] = a.freq[i] + b.freq[i];
        }
    }
  }
  
  static class LazySegment {
    int n;
    int h;
    Frequency[] tree;
    int[] lazy;

    public LazySegment(int n) {
      this.n = n;
      h = 32 - Integer.numberOfLeadingZeros(n);
      int base = (1 << h);
      tree = new Frequency[base << 1];
      lazy = new int[base << 1];
    }

    public void init(char[] arr) {
      for (int i = 0; i < arr.length; i++) {
        tree[n + i] = new Frequency(arr[i]);
      }
      tree[0] = new Frequency();
      for (int i = n - 1; i > 0; --i) {
          tree[i] = new Frequency(tree[i << 1], tree[i << 1 | 1]);
      }
    }
    
    public void updateRange(int l, int r, int value) {
        r++;
      if (value == 0) {
          return;
      }
      push(l, l + 1);
      push(r - 1, r);
      boolean cl = false;
      boolean cr = false;
      for (l += n, r += n; l < r; l >>= 1, r >>= 1) {
        if (cl) {
          calc(l - 1);
        }
        if (cr) {
          calc(r);
        }
        if ((l & 1) > 0) {
          apply(l++, value);
          cl = true;
        }
        if ((r & 1) > 0) {
          apply(--r, value);
          cr = true;
        }
      }
      for (--l; r > 0; l >>= 1, r >>= 1) {
        if (cl) {
          calc(l);
        }
        if (cr && (!cl || l != r)) {
          calc(r);
        }
      }
    }

    Frequency getSum(int l, int r) {
        r++;
      push(l, l + 1);
      push(r - 1, r);
      Frequency res = new Frequency();
      for (l += n, r += n; l < r; l >>= 1, r >>= 1) {
        if ((l & 1) > 0) {
          res.sum(tree[l++]);
        }
        if ((r & 1) > 0) {
          res.sum(tree[--r]);
        }
      }
      return res;
    }

    private void calc(int p) {
      if (lazy[p] == 0) {
        tree[p].sum(tree[p << 1], tree[p << 1 | 1]);
      } else {
          tree[p].shift(lazy[p]);
      }
    }

    private void apply(int p, int value) {
      tree[p].shift(value);
      if (p < n) {
        lazy[p] += value;
      }
    }

    private void push(int l, int r) {
      int s = h;
      for (l += n, r += n - 1; s > 0; --s) {
        for (int i = l >> s; i <= r >> s; i++) {
          if (lazy[i] != 0) {
            apply(i << 1, lazy[i]);
            apply(i << 1 | 1, lazy[i]);
            lazy[i] = 0;
          }
        }
      }
    }
  }
  
  public static long power(long a, long n) {
    if (n < 0) {
      return power(power(a, MOD - 2), -n);
    }
    if (n == 0) {
      return 1;
    }
    if (n == 1) {
      return a;
    }

    long r = 1;
    for (; n > 0; n >>= 1, a = (a*a) % MOD) {
      if ((n & 1) > 0) {
        r = (r*a) % MOD;
      }
    }
    return r;
  }

  static long mul(long a, long b) {
    return (a * b) % MOD;
  }

  static long div(long a, long b) {
      return  (a * power(b, -1)) % MOD;
  }
  
  public static void main(String[] args) throws IOException {
    BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
    BufferedWriter bw = new BufferedWriter(new FileWriter(System.getenv("OUTPUT_PATH")));

    StringTokenizer st = new StringTokenizer(br.readLine());
    int n = Integer.parseInt(st.nextToken());
    int q = Integer.parseInt(st.nextToken());

    char[] s = br.readLine().toCharArray();

    for (int i = 0; i < s.length; i++) {
      s[i] -= 'a';
    }
    
    LazySegment tree = new LazySegment(s.length);
    tree.init(s);

    for (int i = 0; i < q; i++) {
      st = new StringTokenizer(br.readLine());
      int c = Integer.parseInt(st.nextToken());
      int left = Integer.parseInt(st.nextToken());
      int right = Integer.parseInt(st.nextToken());
      if (c == 1) {
        int x = (int) (Long.parseLong(st.nextToken()) % MAX);
        if (x > 0) {
            tree.updateRange(left, right, x);
        }
      } else {
        int[] freq = tree.getSum(left, right).freq;        
        long even = 1;
        for (int j = 0; j < freq.length; j++) {
          if (freq[j] > 0) {
            even = mul(even, power(2, freq[j] - 1));
          }
        }
        long ans = (MOD + even - 1) % MOD;
        for (int j = 0; j < freq.length; j++) {
          if (freq[j] > 0) {
              long m = power(2, freq[j] - 1);
            ans += mul(div(even, m), m);
          }
        }
        ans %= MOD;
        bw.write(ans + "\n");
      }
    }

    bw.close();
    br.close();
  }
}
