# Enter your code here. Read input from STDIN. Print output to STDOUT
from collections import defaultdict
#defaultdict is similar to a normal library except keys have default values if they haven't been set already
import sys
d=defaultdict(list)
lst=list(map(int, input().split()))
n=lst[0]
m=lst[1]
for i in range(n):
    d[sys.stdin.readline().strip()].append(i+1)

for i in range(m):
    l = d[sys.stdin.readline().strip()]
    if l: print(*l)
    else: print(-1)
    
