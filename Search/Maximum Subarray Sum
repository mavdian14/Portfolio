#!/bin/python3

import math
import os
import random
import re
import sys
import bisect
import itertools

def maximumSum(a, m):
    #accumulate object. Return series of accumulated sums (or other binary function results).
    a = list(map(lambda x:x%m,itertools.accumulate(a)))
    maxi = max(a)
    arr = []
    for i in a:
        bisect.insort(arr,i)
        if i!=arr[-1]:
            maxi = max(maxi,(i-arr[bisect.bisect_right(arr,i)])%m)
    return maxi

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    q = int(input().strip())

    for q_itr in range(q):
        first_multiple_input = input().rstrip().split()

        n = int(first_multiple_input[0])

        m = int(first_multiple_input[1])

        a = list(map(int, input().rstrip().split()))

        result = maximumSum(a, m)

        fptr.write(str(result) + '\n')

    fptr.close()
