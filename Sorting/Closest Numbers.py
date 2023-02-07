#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'closestNumbers' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts INTEGER_ARRAY arr as parameter.
#

def closestNumbers(arr):
    pairs = []
    mindiff = 999999999999
    arr.sort()
    
    for i in range(1, len(arr)):
        d = abs(arr[i-1]-arr[i])
        #new min mindiff
        if d < mindiff:
            mindiff=d
            pairs = [arr[i-1],arr[i]]
        elif d == mindiff:
            #extend() add all elements of an iterable to the end of the list
            pairs.extend([arr[i-1], arr[i]])
    
    return pairs
            
            

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    result = closestNumbers(arr)

    fptr.write(' '.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
