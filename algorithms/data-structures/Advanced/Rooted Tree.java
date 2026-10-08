import java.io.*;
import java.util.*;

public class Solution {
    
    static final int D = 17;
  static final int MOD = 1_000_000_007;
  static List<Integer>[] e;
  static int[][] par;
  static int[][] fenwick;
  static int[] dep;
  static int[] dfnl;
  static int[] dfnr;
  static int tick = 0;
  

  static int lowestCommonAncestor(int u, int v) {
    if (dep[u] < dep[v]) {
      int temp = u;
      u = v;
      v = temp;
    }
    for (int i = D; --i >= 0; ) {
      if (dep[u]-(1<<i) >= dep[v]) {
        u = par[i][u];
      }
    }
    if (u == v) {
      return u;
    }
    for (int i = D; --i >= 0; ) {
      if (par[i][u] != par[i][v]) {
        u = par[i][u];
        v = par[i][v];
      }
    }
    return par[0][u];
  }
  
  static class Node {
    int u;
    int p;
    boolean start = true;
    Node(int u, int p) {
      this.u = u;
      this.p = p;
    }
  }
  
  static void dfs(int u, int p) {
    Deque<Node> queue = new LinkedList<>();
    queue.add(new Node(u, p));
    while (!queue.isEmpty()) {
      Node node = queue.peek();
      if (node.start) {
        dfnl[node.u] = tick++;
        for (int v: e[node.u]) {
          if (v != node.p) {
            par[0][v] = node.u;
            dep[v] = dep[node.u]+1;
            queue.addFirst(new Node(v, node.u));
          }
        }
        node.start = false;
      } else {
        dfnr[node.u] = tick;
        queue.remove();
      }
    }
  }

  static void add(int fenwick[], int x, int v) {
    for (; x < fenwick.length; x |= x+1) {
      fenwick[x] = (fenwick[x] + v) % MOD;
    }
  }

  static int getSum(int fenwick[], int x) {
    int s = 0;
    for (; x > 0; x &= x-1)
      s = (s + fenwick[x-1]) % MOD;
    return s;
  }

  static int get(int u) {
    long pw = 1;
    long s = 0;
    for (int i = 0; i < 3; i++) {
      s = (s + pw * getSum(fenwick[i], dfnl[u]+1)) % MOD;
      pw = (pw * dep[u]) % MOD;
    }
    return (int) (((MOD+1l) / 2 * s)%MOD);
  }


  static int query(int u, int v) {
    int w = lowestCommonAncestor(u, v);
    long s = ((long)(get(u))+get(v)-get(w))%MOD;
    if (par[0][w] >= 0) {
      s = (s - get(par[0][w])) % MOD;
    }
    return (int) s;
  }

  static void upd(int fenwick[], int l, int r, int v) {
    add(fenwick, l, v);
    add(fenwick, r, -v);
  }

  static void update(int u, int x, int y) {
    int l = dfnl[u];
    int r = dfnr[u];
    upd(fenwick[2], l, r, y);
    upd(fenwick[1], l, r, (int)(((long)(1 - 2 * dep[u]) * y + 2l * x) % MOD));
    upd(fenwick[0], l, r, (int)((dep[u] * (dep[u] - 1l) * y + 2 * (1l - dep[u]) * x) % MOD));
  }
  
  public static void main(String[] args) throws IOException {
    BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
    BufferedWriter bw = new BufferedWriter(new FileWriter(System.getenv("OUTPUT_PATH")));

    StringTokenizer st = new StringTokenizer(br.readLine());
    int n = Integer.parseInt(st.nextToken());
    int m = Integer.parseInt(st.nextToken());
    int rt = Integer.parseInt(st.nextToken())-1;

    
    e = new List[n];
    for (int i = 0; i < n; i++) {
      e[i] = new LinkedList<>();
    }
    for (int i = 0; i < n-1; i++) {
      st = new StringTokenizer(br.readLine());
      int u = Integer.parseInt(st.nextToken())-1;
      int v = Integer.parseInt(st.nextToken())-1;
      e[u].add(v);
      e[v].add(u);
    }

    dep = new int[n];
    par = new int[D][n];
    dfnl = new int[n];
    dfnr = new int[n];

    tick = 0;
    dep[rt] = 0;
    par[0][rt] = -1;
    dfs(rt, -1);

    for (int k = 1; k < D; k++) {
      for (int i = 0; i < n; i++) {
        par[k][i] = par[k-1][i] == -1 ? par[k-1][i] : par[k-1][par[k-1][i]];
      }
    }

    fenwick = new int[3][n];
        
    while (m-- > 0) {
      st = new StringTokenizer(br.readLine());
      char op = st.nextToken().charAt(0);
      int u = Integer.parseInt(st.nextToken()) - 1;
      int v = Integer.parseInt(st.nextToken());
      if (op == 'Q') {
        v--;
        int result = (query(u, v)+MOD)%MOD;
        bw.write(result + "\n");
      } else {
        int w = Integer.parseInt(st.nextToken());
        update(u, v, w);
      }
    }
    
    bw.newLine();
    bw.close();
    br.close();
  }
}
