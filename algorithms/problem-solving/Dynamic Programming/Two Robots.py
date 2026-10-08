#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'twoRobots' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER m
#  2. 2D_INTEGER_ARRAY queries
#

def twoRobots(m, queries):
    prev_bot = queries[0][0]
    mintotal = 0
    containers = [0]*(m+1)

    for a,b in queries:
        distance = abs(a-b)
        traveled = abs(prev_bot-a)+distance

        minimums = min(abs(k-a)+v for k,v in enumerate(containers))
        minimums = min(mintotal,minimums)
        mintotal += traveled
        
        # arr[:] is slice notation, if arr is a list it creates a shallow copy. If arr is a tuple/str it does nothing.
        containers[:] = [ v+traveled for v in containers ]
        containers[prev_bot] = minimums+distance
        prev_bot = b

    return min(containers)

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input())
    
    for x in range(t):
        mn = input().split()

        m = int(mn[0])

        n = int(mn[1])

        queries = []

        for _ in range(n):
            queries.append(list(map(int, input().rstrip().split())))

        result = twoRobots(m, queries)

        fptr.write(str(result) + '\n')

    fptr.close()
