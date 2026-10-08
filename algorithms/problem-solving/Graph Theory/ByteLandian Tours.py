#!/bin/python3

import math
import os
import random
import re
import sys

import math
def tours(adj, N):
    facts = [0]*N
    z=0
    for i in range(len(adj)):
        vertList = adj[i]
        z_count = 0
        nz_count = 0
        for neighbor in vertList:
            if len(adj[neighbor]) == 1:
                facts[i] += 1
                z_count += 1
                z+= 1
            else:
                nz_count += 1
            if nz_count > 2:
                return 0
    sum = 1
    for num in facts:
        sum = (sum * math.factorial(num)) % 1000000007
    if z == N-1:
        return sum
    return (2*sum)% 1000000007
    
T = int(input())
for i in range(T):
    N = int(input())
    adj = [[] for i in range(N)]
    for x in range(1, N):
        road = list(map(int,input().split()))
        adj[road[0]].append(road[1])
        adj[road[1]].append(road[0])
    print(tours(adj, N))
