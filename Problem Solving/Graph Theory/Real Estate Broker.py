#!/bin/python3

import os
import sys

def kuhn(v):
    global house, used, buyers
    if used[v]: 
        return False
    used[v] = True
    for buyer in buyers[v]:
        if (house[buyer] == -1 or kuhn(house[buyer])):
            house[buyer] = v
            return True
    return False
    
############################################

sys.setrecursionlimit(30000)   

n, m = map(int, input().strip().split())

#clients (n)
a = []
p = []
for i in range(n):
    q, w = map(int, input().strip().split())
    a.append(q)
    p.append(w)

#houses (m)
buyers = [[] for i in range(m)]
for i in range(m):
    x, y = map(int, input().strip().split())
    for j in range(n):
        if x > a[j] and y <= p[j]:
            buyers[i].append(j)

#########################################

house = [-1] * (n)           
for i in range(m):
    used = [False] * (m)
    kuhn(i)

res = 0
for h in house:
    if (h >= 0):
        res += 1

print(res)
