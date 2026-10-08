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

public class DigitsSquareBoard {
    static final int  max = 60;
    static final int  maxn = 30;
    static int[][]a;
    static int n;
    static int[][][][]g;
    
    public static void main(String[] args) throws IOException{
        new DigitsSquareBoard().run();
    }
    
    public void run() throws IOException{
        Scanner in = new Scanner(System.in);
        BufferedWriter log = new BufferedWriter(new OutputStreamWriter(System.out));
        int t = in.nextInt();
        int i,j,k,l,m;
        a = new int[maxn][maxn];
        g = new int[max][max][max][max];

        for(int tt =0;tt < t;tt++){
            n = in.nextInt();
            for(i=0;i<n;i++){
                Arrays.fill(a[i],-1);
            }
            for(i=0;i<n;i++){
                for(j=0;j<n;j++){
                    m = in.nextInt();
                    a[i][j]=(m==2||m==3||m==5||m==7)?0:1;//0 == black primes
                }
            }

            for(i=0;i<max;i++){
                for(j=0;j<max;j++){
                    for(k=0;k<max;k++){
                        for(l=0;l<max;l++){
                            g[i][j][k][l]=-1;
                        }
                    }
                }
            }
            int nimsum = grundy(0,0,n-1,n-1);

            if(nimsum>0) log.write("First\n");
            else log.write("Second\n");
        }
        log.flush();
    }
    
    public boolean prime(int x, int y, int z, int t){
        int i,j;
        for(i=x;i<=z;i++){
                for(j=y;j<=t;j++){
                    if(a[i][j]==1) return false;
                }
            }
        return true;
    }
              
    public int grundy(int x, int y, int z, int t){
        if (g[x][y][z][t]!=-1) return g[x][y][z][t];
        if (prime(x,y,z,t)) {
            g[x][y][z][t]=0;
            return 0;
        }

        ArrayList<Integer> min = new ArrayList<Integer>();
        int i,j,k;

        for(i=x+1;i<=z;i++){
            k = grundy(x,y,i-1,t)^grundy(i,y,z,t);
            if(!min.contains(k)) min.add(k);
        }

        for(i=y+1;i<=t;i++){
            k = grundy(x,y,z,i-1)^grundy(x,i,z,t);
            if(!min.contains(k)) min.add(k);
        }

        for(k=0;min.contains(k);k++);


        g[x][y][z][t]=k;
        return k;
    }
    
}
