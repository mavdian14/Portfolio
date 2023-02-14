#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'minimumAbsoluteDifference' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER_ARRAY arr as parameter.
#

def minimumAbsoluteDifference(arr):
    arr.sort()
    #if the array is sorted don't need to run a nested for loop comparing the each element to each other as each elements min_diff will be with element to the left or to the right of itself
    min_diff=sys.maxsize
    for i in range(1,len(arr)):
        min_diff = min(min_diff, abs(arr[i-1]-arr[i]))
    return min_diff

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    result = minimumAbsoluteDifference(arr)

    fptr.write(str(result) + '\n')

    fptr.close()
