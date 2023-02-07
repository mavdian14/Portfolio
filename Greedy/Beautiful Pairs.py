#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'beautifulPairs' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER_ARRAY A
#  2. INTEGER_ARRAY B
#
from collections import Counter
def beautifulPairs(A, B):
    # Write your code here
    a=Counter(A)
    b=Counter(B)
    #counter for all the unique matches of              A[i]=B[j]
    b_set=0
    
    #check keys in A & B, set b_set to the min occurences of that key in A or B
    for val in a:
        if val in b:
            b_set+=min(a[val],b[val])
    
    if b_set==len(A):
        return b_set-1
    else:
        return b_set+1

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    A = list(map(int, input().rstrip().split()))

    B = list(map(int, input().rstrip().split()))

    result = beautifulPairs(A, B)

    fptr.write(str(result) + '\n')

    fptr.close()
