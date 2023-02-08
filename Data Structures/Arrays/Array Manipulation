#!/bin/python3

import math
import os
import random
import re
import sys


def arrayManipulation(n, queries):
    a = [0 for i in range(n)]
    for j in queries:
        a[j[0]-1]+=j[2]
        if j[1]!=n:
            a[j[1]]-=j[2]
    maxi = 0
    cur = 0
    for k in range(len(a)):
        cur += a[k]
        if cur>maxi:
            maxi=cur
    return maxi

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    m = int(first_multiple_input[1])

    queries = []

    for _ in range(m):
        queries.append(list(map(int, input().rstrip().split())))

    result = arrayManipulation(n, queries)

    fptr.write(str(result) + '\n')

    fptr.close()
