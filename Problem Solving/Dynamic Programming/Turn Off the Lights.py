#!/bin/python3

import math
import os
import random
import re
import sys

def get_sum(s, c, k, t):
    v = None
    for p in range(s, len(c), 2 * k + 1):
        print(p, end=' ')
        if v:
            t += 2 * k + 1
        else:
            v = 0
        v += c[p]
    if t < len(c):
        v = None
    print(' => ', v, 't=', t)
    return v
def turnOffTheLights(k, c):
    mm = None
    for s in range(k + 1):
        summ = get_sum(s, c, k, k + 1 + s)
        if not mm or (summ and mm > summ):
            mm = summ
    return mm

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    k = int(first_multiple_input[1])

    c = list(map(int, input().rstrip().split()))

    result = turnOffTheLights(k, c)

    fptr.write(str(result) + '\n')

    fptr.close()
