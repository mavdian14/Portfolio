#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'largestPermutation' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts following parameters:
#  1. INTEGER k
#  2. INTEGER_ARRAY arr
#

def largestPermutation(k, arr):
    index={} #element: index
    n=len(arr)
    for i in range(n):
        index[arr[i]] = i
    
    swaps = i = 0
    
    while swaps < k and i < n:
        if arr[i] < n-i:
            #swap operation of elements
            idx = index[n-i]
            arr[i], arr[idx] = arr[idx], arr[i]
            #update index dictionary
            index[arr[idx]] = idx
            index[n-i] = i
            swaps+=1
        i+=1
    return arr
            

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    k = int(first_multiple_input[1])

    arr = list(map(int, input().rstrip().split()))

    result = largestPermutation(k, arr)

    fptr.write(' '.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
