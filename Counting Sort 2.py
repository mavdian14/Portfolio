#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'countingSort' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts INTEGER_ARRAY arr as parameter.
#

def countingSort(arr):
    count=[0]*(max(arr)+1)
    
    for i in arr:
        count[i]+=1
    
    sortarr = []
    #go thru count from counting sort 1, for each a[i] where a[i]!=0, reduce it all the way to zero in increments of 1, add that index into sortarr & continue until all of count is [0]
    for i in range(len(count)):
        while count[i]!=0:
            count[i]-=1
            sortarr.append(i)
    
    return sortarr
            

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    result = countingSort(arr)

    fptr.write(' '.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
