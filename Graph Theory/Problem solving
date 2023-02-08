#!/bin/python3

import math
import os
import random
import re
import sys

T = int(input())
for _ in range(T):
    N, K = map(int, input().split())
    vi = list(map(int, input().split()))

    m = [None] * N
    def match(s):
        if v[s]: return False
        v[s] = True
        for i in range(s+1, N):
            if abs(vi[i] - vi[s]) < K: continue
            if m[i] == None or match(m[i]):
                m[i] = s
                return True
        return False

    mc = 0
    for i in range(N):
        v = [False] * N
        if match(i): mc += 1
    print(N - mc)
