#!/bin/python3

import math
import os
import random
import re
import sys

r, c = map(int, input().strip().split())
n = max(r, c)
g = [[0] * n for i in range(n)]
for i in range(r):
    bs = list(map(int, input().strip().split()))
    for j in range(c):
        g[i][j] = bs[j]
x = [[0] * (n + 1) for i in range(n + 1)]
for i in range(n):
    for j in range(n):
        x[i + 1][j + 1] = x[i + 1][j] + x[i][j + 1] - x[i][j] + g[i][j]
fs  = g
fz  = [[0] * n for i in range(n)]
ans = [[0] * n for i in range(n)]
anz = [[0] * n for i in range(n)]
for d in range(1, n):
    for i in range(n - d):
        I = i + d + 1
        for j in range(n-d):
            J = j + d + 1
            total = fz[i][j] = x[I][J] - x[i][J] - x[I][j] + x[i][j]
            anz[i][j] = min(
                ans[i][j] + d * (total - fs[i][j]),
                ans[i][j + 1] + d * (total - fs[i][j + 1]),
                ans[i + 1][j] + d * (total - fs[i + 1][j]),
                ans[i + 1][j + 1] + d*(total - fs[i + 1][j + 1]))
    ans, anz = anz, ans
    fs, fz =  fz, fs
print(ans[0][0])
