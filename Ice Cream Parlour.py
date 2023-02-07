#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'icecreamParlor' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts following parameters:
#  1. INTEGER m
#  2. INTEGER_ARRAY arr
#

def icecreamParlor(m, arr):
    n = len(arr)
    result = []
    #sum counter that should equal m
    s = 0
    #the for loop traverses backwards
    for i in range(n-1, 0,-1):
        if arr[i] < m:
            #work from all j less than i as i will be >= j
            for j in range(i):
                temp = arr[i]+arr[j]
                if temp == m:
                    result = [j+1, i+1]
                    break
    return result

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        m = int(input().strip())

        n = int(input().strip())

        arr = list(map(int, input().rstrip().split()))

        result = icecreamParlor(m, arr)

        fptr.write(' '.join(map(str, result)))
        fptr.write('\n')

    fptr.close()
