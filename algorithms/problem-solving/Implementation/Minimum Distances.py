#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'minimumDistances' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER_ARRAY a as parameter.
#

def minimumDistances(a):
    res =-1
    memo=[-1]*(10**5 +3) #max value of a[i] and elements in a
    #enumerate(a) in this case puts a counter for each indice in a: 0-len(a) i.e. a tuple-list/dictionary with the elements of a with keys corresponding to the occurence of that element in a
    for i,el in enumerate(a):
        if memo[el] >= 0:
            res = min(res if res >=0 else 10**5 +2, i-memo[el])
        memo[el]=i
    return res
        

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    a = list(map(int, input().rstrip().split()))

    result = minimumDistances(a)

    fptr.write(str(result) + '\n')

    fptr.close()
