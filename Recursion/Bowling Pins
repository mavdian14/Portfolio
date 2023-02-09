#!/bin/python3

import math
import os
import random
import re
import sys

g = {0:0,1:1,2:2}
for i in range(3,301):
    found = set()
    for j in range(i-1):
        found.add(g[j]^g[i-j-1])
        found.add(g[j]^g[i-j-2])
    g[i] = min(set(range(max(found)+2))-found)
def isWinning(n, config):
    tot = 0
    L = 0
    config += "X"
    for i in config:
        if i == "I":
            L+=1
        else:
            tot = tot^g[L]
            L = 0
    if tot != 0:
        return "WIN"
    return "LOSE"

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input())

    for t_itr in range(t):
        n = int(input())

        config = input()

        result = isWinning(n, config)

        fptr.write(result + '\n')

    fptr.close()
