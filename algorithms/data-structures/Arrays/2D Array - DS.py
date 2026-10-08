#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'hourglassSum' function below.
#
# The function is expected to return an INTEGER.
# The function accepts 2D_INTEGER_ARRAY arr as parameter.
#

def hourglassSum(arr):
    maxsum = -99
    #range is 4 for rows and columns because we only want to iterate over the values in the inner 4x4 grid as they aren't boundary values, so they can be the center of an hourglass
    for i in range(4):
        for j in range(4):
            #top value sum
            top = sum(arr[i][j:j+3])
            mid = arr[i+1][j+1]
            bottom = sum(arr[i+2][j:j+3])
            
            #total sum
            hourglass = top + mid + bottom
            maxsum = max(hourglass, maxsum)
    
    return maxsum

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    arr = []

    for _ in range(6):
        arr.append(list(map(int, input().rstrip().split())))

    result = hourglassSum(arr)

    fptr.write(str(result) + '\n')

    fptr.close()
