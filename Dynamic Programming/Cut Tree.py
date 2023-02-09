#!/bin/python3

import os
import sys
from collections import defaultdict
#
# Complete the cuttree function below.
#

def cuttree(n, k, edges):
    g = [[] for _ in range(n)]
    for i in edges:
        g[i[0]-1].append(i[1]-1)
        g[i[1]-1].append(i[0]-1)
    global ans
    ans = 1
    def multiply(x, y):
        ans = defaultdict(lambda: 0)
        for k, v in x.items():
            for k1, v1 in y.items(): ans[k+k1-1] += v*v1
        for k, v in ans.items():
            if k in x: x[k] += v
            else: x[k] = v
    def dfs(i,p):
        global ans
        if g[i] == [p]:
            ans += 1
            return {0:1}
        x = 1 if i else 0
        res = {len(g[i])-x : 1}
        for nxt in g[i]:
            if nxt != p: multiply(res, dfs(nxt, i))
        ans += sum(((v if i+x <= k else 0) for i, v in res.items()))
        return res
    dfs(0,-1)
    return ans
          
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    nk = input().split()

    n = int(nk[0])

    k = int(nk[1])

    edges = []

    for _ in range(n-1):
        edges.append(list(map(int, input().rstrip().split())))

    result = cuttree(n, k, edges)

    fptr.write(str(result) + '\n')

    fptr.close()
