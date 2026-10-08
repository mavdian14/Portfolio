#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'bonetrousle' function below.
#
# The function is expected to return a LONG_INTEGER_ARRAY.
# The function accepts following parameters:
#  1. LONG_INTEGER n
#  2. LONG_INTEGER k
#  3. INTEGER b

#n = sticks of spaghetti, b = num of boxes, k = num of diff box sizes

def bonetrousle(n, k, b):
    if not(b*(b+1)) <= 2*n <= b*(2*k-b+1): 
        yield -1
        return
    s=b*(b-1)//2
    i=min(k,n-s)
    while b:
        yield i
        n-=i
        b-=1
        s-=b
        i=min(i-1,n-s)
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        first_multiple_input = input().rstrip().split()

        n = int(first_multiple_input[0])

        k = int(first_multiple_input[1])

        b = int(first_multiple_input[2])

        result = bonetrousle(n, k, b)

        fptr.write(' '.join(map(str, result)))
        fptr.write('\n')

    fptr.close()
