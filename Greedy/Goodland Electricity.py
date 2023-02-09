#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'pylons' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER k
#  2. INTEGER_ARRAY arr
#

def pylons(k, arr):
    count = i = 0
    loc = i + k -1
    while i < n:
        #if city is eligible for power plant
        if arr[loc] == 1:
            i = loc + k
            loc = i + k -1
            count+=1
            if loc >= n:
                loc = n-1
        else:
            loc -=1
            if loc < i - k +1 or loc < 0:
                return -1
    
    return count

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    k = int(first_multiple_input[1])

    arr = list(map(int, input().rstrip().split()))

    result = pylons(k, arr)

    fptr.write(str(result) + '\n')

    fptr.close()
