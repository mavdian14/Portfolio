#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'summingPieces' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER_ARRAY arr as parameter.
#
MOD = 10**9 +7

def summingPieces(arr):
    n = len(arr)
    t=0
    q=0
    s=0
    T=1
    z=1
    
    for i in arr:
        s = (2*s+T*i+q)%MOD
        q = (q+z*i)%MOD
        if t == 0: t=1
        else: t = (t*2)%MOD
        z = (z+t)%MOD
        T=(T+z)%MOD
    return s   

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    arr_count = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    result = summingPieces(arr)

    fptr.write(str(result) + '\n')

    fptr.close()
