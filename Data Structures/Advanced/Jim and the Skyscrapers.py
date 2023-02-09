#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'solve' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER_ARRAY arr as parameter.
#

def solve(arr):
    #max num of skycrapers in arr
    arr.append(2**64)
    idx,routes = 0,0
    stack,m = [], {}
    while idx < len(arr):
        if stack == [] or arr[idx] <= stack[-1]:
            stack.append(arr[idx])
            if arr[idx] in m:
                m[arr[idx]]+=1
            else:
                m[arr[idx]] = 1
            idx +=1
        else:
            top = stack.pop()
            if top in m and top< arr[idx]:
                routes += m[top]*(m[top]-1)
                del m[top]
    return routes
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    arr_count = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    result = solve(arr)

    fptr.write(str(result) + '\n')

    fptr.close()
