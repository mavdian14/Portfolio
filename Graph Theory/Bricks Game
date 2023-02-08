#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'bricksGame' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER_ARRAY arr as parameter.
#

def bricksGame(arr):
    n=len(arr)
    if n < 4:
        return sum(arr)
    rev=arr[::-1]
    score=[0]*n
    sums=[0]*n
    
    sums[0] = score[0] = rev[0]
    sums[1] = score[1] = rev[0] + rev[1]
    sums[2]= score[2] = rev[0] + rev[1] + rev[2]
    
    for i in range(3,n):
        sums[i] = sums[i-1] + rev[i]
        
        b1= rev[i] + sums[i-1] - score[i-1]
        b2= rev[i-1] + rev[i] + sums[i-2] - score[i-2]
        b3= rev[i-2] + rev[i-1] + rev[i] + sums[i-3] - score[i-3]
        
        score[i] = max(b1,b2,b3)
    
    return score[-1]

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        arr_count = int(input().strip())

        arr = list(map(int, input().rstrip().split()))

        result = bricksGame(arr)

        fptr.write(str(result) + '\n')

    fptr.close()
