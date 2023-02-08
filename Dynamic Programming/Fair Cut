#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'fairCut' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER k
#  2. INTEGER_ARRAY arr
#

def fairCut(k, arr):
    if n - k < k:
        k = n - k
    arr.sort()
    isevenn = n % 2 == 0
    isevenk = k % 2 == 0
    
    indices = []
    if (isevenn and isevenk) or (not isevenn and isevenk):
        x = (n+1)//2
        for i in range(k//2):
            indices.append(x-(2*i+1))
            indices.append(x+(2*i+1))
    if (isevenn and not isevenk) or (not isevenn and not isevenk):
        x = (n+1)//2
        indices = [x]
        for i in range(k//2):
            indices.append(x-(2*(i+1)))
            indices.append(x+(2*(i+1)))
    
    s1 = []
    s2 = []
    
    for i in range(0, n):
        if i + 1 in indices:
            s1.append(arr[i])
        else:
            s2.append(arr[i])

    sum = 0
    for i in s1:
        for j in s2:
            sum += abs(i - j)
    return sum
    
    return sum

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    k = int(first_multiple_input[1])

    arr = list(map(int, input().rstrip().split()))

    result = fairCut(k, arr)

    fptr.write(str(result) + '\n')

    fptr.close()
