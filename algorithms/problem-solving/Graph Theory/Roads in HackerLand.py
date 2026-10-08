#!/bin/python3

import math
import os
import random
import re
import sys

p = list(range(10 ** 5))

def dsu_get(v):
    if p[v] != v: p[v] = dsu_get(p[v])
    
    return p[v]

def dsu_merge(u, v):
    u = dsu_get(u)
    v = dsu_get(v)
    p[u] = v
    
    return u != v

n, m = map(int, input().split())
e = []
for i in range(m):
    a, b, c = map(int, input().split())
    e += [(c, b - 1, a - 1)]

e.sort()

G = [[] for x in range(n)]
for c, a, b in e:
    if dsu_merge(a, b):
        G[a] += [(b, c)]
        G[b] += [(a, c)]

f = [0] * m
def dfs(v, par = -1):
    sz = 1
    for u, c in G[v]:
        if u == par: continue
        
        y = dfs(u, v)
        
        f[c] = y * (n - y)
        sz += y
    
    return sz

dfs(0)

ans = 0
for x in f[::-1]:
    ans *= 2
    ans += x

print(bin(ans)[2:])
