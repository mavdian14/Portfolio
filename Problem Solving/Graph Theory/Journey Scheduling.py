#!/bin/python3

import math
import os
import random
import re
import sys

from heapq import *

def read():
    return map(int, input().split())

def read_graph(N, M):
    G = [[] for _ in range(N)]
    for _ in range(M):
        u, v = map(int, input().split())
        u, v = u-1, v-1
        G[u].append((1, v))
        G[v].append((1, u))
    return G

def dykstra(G, s, c0=0, f_cost=lambda a,b:a+b):
    N = len(G)
    cost = [None] * N
    path = [None] * N
    h = [(c0, None, s, None)]
    while len(h) != 0:
        c, m, n, p = heappop(h)
        if cost[n] != None: continue
        cost[n] = c
        path[n] = (m, p)
        for m2, n2 in G[n]:
            if cost[n2] != None: continue
            heappush(h, (f_cost(c, m2), m2, n2, n))
    return cost, path

def dfs(n0, d0):
    global G
    global dist
    q = [(n0, d0)]
    while len(q) != 0:
        n,d = q.pop()
        for m, n2 in G[n]:
            if dist[n2] != -1: continue
            dist[n2] = d+1
            q.append((n2, d+1))

N, M = read()
G = read_graph(N, N-1)

# both ends(s,t) of diameter
c,p = dykstra(G,0)
s = c.index(max(c))
c,p = dykstra(G,s)
t = c.index(max(c))

# length of diameter
n, diam = t, 0
while p[n][1] != None:
    diam += 1
    n = p[n][1]

# find middle point of diameter
n1, n2 = t, p[t][1]
for i in range(diam//2):
    n1 = p[n1][1]
    n2 = p[n2][1]

# distance from middle point
dist = [-1] * N
if diam % 2 == 0:
    dist[n1] = 0
    dfs(n1, 0)
else:
    dist[n1] = 0
    dist[n2] = 0
    dfs(n1, 0)
    dfs(n2, 0)

for i in range(M):
    v,k = read()
    print(dist[v-1] + (diam+1)//2 + (k-1)*diam)
