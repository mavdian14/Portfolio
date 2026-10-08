#!/bin/python3

import math
import os
import random
import re
import sys
from collections import deque
from collections import defaultdict

n,e = [int(x) for x in input().split()]

kop = defaultdict(set)
gran = defaultdict(list)
for _ in range(e):
    x,y,k = [int(x) for x in input().split()]
    kop[(x-1,y-1)].add(k%10)
    kop[(y-1,x-1)].add(10 - (k%10))
    gran[x-1].append(y-1)
    gran[y-1].append(x-1)

    
out = [0]*10
founder = [[0]*n for _ in range(10)]
found = [False]*n
for i in range(n):
    if found[i]:
        continue
    que = deque()
    que.append((i,0))
    cluster = set()
    
    while len(que)>0:
        j,col = que.pop()
        if founder[col][j]==1:
            continue
        founder[col][j] = 1
        found[j] = True
        cluster.add(j)
        for k in gran[j]:
            for kost in kop[(j,k)]:
                que.append((k,(kost+col)%10))
    if founder[1][i] == 1:
        cycle = 1
        for d in range(10):
            out[d]+=len(cluster)*(len(cluster)-1)
    elif founder[2][i] == 1:
        cycle = 2
    elif founder[5][i] == 1:
        cycle = 5
    else:
        cycle = 0
    firstc = [set() for _ in range(10)]
    for node in cluster:
        for ind in range(10):
            if founder[ind][node]==1:
                firstc[ind].add(node)
                break
                
    dig = [0]*10
    for d1 in range(10):
        for d2 in range(10):
            if d1 != d2:
                dig[(d2-d1)%10] += len(firstc[d1])*len(firstc[d2])
            else:
                dig[0] += len(firstc[d1])*(len(firstc[d1])-1)
    #print(dig,cycle)            
    if cycle==2:
        summaEv = dig[0]+dig[2]+dig[4]+dig[6]+dig[8]
        for d in [0,2,4,6,8]:
            out[d]+=summaEv
        summaOdd = dig[1]+dig[3]+dig[5]+dig[7]+dig[9]
        for d in [1,3,5,7,9]:
            out[d]+=summaOdd
    elif cycle==5:
        
        summa0 = dig[0] + dig[5]
        summa1 = dig[1] + dig[6]
        summa2 = dig[2] + dig[7]
        summa3 = dig[3] + dig[8]
        summa4 = dig[4] + dig[9]
        for d in [0,5]:
            out[d]+=summa0
        for d in [1,6]:
            out[d]+=summa1
        for d in [2,7]:
            out[d]+=summa2
        for d in [3,8]:
            out[d]+=summa3
        for d in [4,9]:
            out[d]+=summa4
    elif cycle==0:
        for d in range(10):
            out[d] += dig[d]
for d in range(10):
    print(out[d])
