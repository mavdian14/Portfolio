#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'arraySplitting' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER_ARRAY arr as parameter.
#
from collections import Counter

def score(lo,hi,ct):
    if (lo+hi)&1: return 0
    elif lo==hi: return ct[lo]-1
    else:
        av=(lo+hi)//2
        if av in ct:
            return 1+max(score(lo,av,ct),score(av,hi,ct))
        else: return 0
    
def arraySplitting(arr):
    c=[0]*len(arr)
    c[0]=arr[0]
    for i in range(1,len(arr)):
        c[i]=c[i-1]+arr[i]
    return score(0,c[-1],Counter(c))
        

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        arr_count = int(input().strip())

        arr = list(map(int, input().rstrip().split()))

        result = arraySplitting(arr)

        fptr.write(str(result) + '\n')

    fptr.close()
