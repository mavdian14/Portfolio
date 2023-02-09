#!/bin/python3

import math
import os
import random
import re
import sys


def sherlockAndMinimax(arr, p, q):
    arr.sort()

    maxInd = p
    minimum = float('inf')
    for ele in arr:
        if abs(ele-p)<minimum:
            minimum = abs(ele-p)
    maximum = minimum

    minimum = float('inf')    
    for i in range(1,len(arr)):
        mid = (arr[i]+arr[i-1])//2
        if p<mid<q:
            minimum = min(mid-arr[i-1],arr[i]-mid)
            if minimum>maximum:
                maximum = minimum
                maxInd = mid

    minimum = float('inf')
    for ele in arr:
        if abs(ele-q)<minimum:
            minimum = abs(ele-q)
    if minimum>maximum:
        maximum = minimum
        maxInd = q

    return maxInd 

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    first_multiple_input = input().rstrip().split()

    p = int(first_multiple_input[0])

    q = int(first_multiple_input[1])

    result = sherlockAndMinimax(arr, p, q)

    fptr.write(str(result) + '\n')

    fptr.close()
