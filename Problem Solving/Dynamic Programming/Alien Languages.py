#!/bin/python3

import math
import os
import random
import re
import sys

mod = 10**8 + 7

for cas in range(int(input())):
    n, m = map(int, input().strip().split())
    v = [2*i > n for i in range(n+1)]
    for i in range(n-1,-1,-1):
        v[i] += v[i + 1]
    c = []
    while v[1]:
        c.append(v[1])
        for i in range(1,n//2+1):
            v[i] = v[2*i]
        for i in range(n//2+1,n+1):
            v[i] = 0
        for i in range(n-1,-1,-1):
            v[i] = (v[i] + v[i + 1]) % mod

    f = [1] + [0]*(len(c)-1)
    for k in range(1,m+1):
        f = [sum(F * C for F, C in zip(f, c)) % mod] + f[:-1]

    print(f[0])
