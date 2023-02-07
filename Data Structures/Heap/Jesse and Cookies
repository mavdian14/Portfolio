#!/bin/python3

import math
import os
import random
import re
import sys
from heapq import heapify, heappush, heappop
#
# Complete the 'cookies' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER k
#  2. INTEGER_ARRAY A
#

def cookies(k, A):
    #heapify() turns an array A that represents a binary tree into a heap data structure
    heapify(A)
    result = 0
    
    #infinite loop
    while True:
        #will pop first/min element
        x = heappop(A)
        
        #base case
        if x >= k:
            return result
    
        #if A non-empty
        if A:
        #x is first element & y is 2nd element in the heap
            y = heappop(A)
            s = x + 2*y
            heappush(A,s)
            result+=1
    #if A has no elements
        else:
            return -1

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    k = int(first_multiple_input[1])

    A = list(map(int, input().rstrip().split()))

    result = cookies(k, A)

    fptr.write(str(result) + '\n')

    fptr.close()
