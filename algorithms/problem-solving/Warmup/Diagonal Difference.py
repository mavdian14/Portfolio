#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'diagonalDifference' function below.
#
# The function is expected to return an INTEGER.
# The function accepts 2D_INTEGER_ARRAY arr as parameter.
#

def diagonalDifference(arr):
    lefttoright = 0
    righttoleft = 0
    for i in range(len(arr)):
        lefttoright+=arr[i][i]
        #column [len(arr)-i-1] gives the right diagonal going down the right diagonal as i increases
        righttoleft+=arr[i][len(arr)-i-1]
    return abs(lefttoright-righttoleft)

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    arr = []

    for _ in range(n):
        arr.append(list(map(int, input().rstrip().split())))

    result = diagonalDifference(arr)

    fptr.write(str(result) + '\n')

    fptr.close()
