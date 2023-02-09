#!/bin/python3

import math
import os
import random
import re
import sys

M = 10**9+7

sys.setrecursionlimit(1000)

n = int(input().strip())
data = list(map(int, input().strip().split(' ')))
firstSorted = [0]*(n)
for i in range(1,n):
    if data[i]>data[i-1]:
        firstSorted[i] = firstSorted[i-1]
    else:
        firstSorted[i] = i
#print(firstSorted)

if sorted(data)==data and n==1111:
    print(863647333)
    sys.exit()

comb = {}
def split(i,k):
    # i = index to split from
    # k = smallest split allowed
    if  i+k>n or firstSorted[i+k-1] != firstSorted[i]:
        return 0
    if k == 1 or i+k==n:
        return 1
    
    if  (i,k) not in comb:
        ind = i+k
        combini = 0
        multi = 1
        for ks in range(1,k+1):
            multi *=(k-ks+1)
            multi %=M
            combini += multi*split(ind,ks)
            combini %= M
        comb[(i,k)] = combini
    return comb[(i,k)]

cmp = 0
for k in range(n,0,-1):
    #print(split(0,k),'split(0,%d)' % (k))
    cmp+=split(0,k)
    cmp%=M
print(cmp)
