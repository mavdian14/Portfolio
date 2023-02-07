#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'luckBalance' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER k
#  2. 2D_INTEGER_ARRAY contests
#

def luckBalance(k, contests):
    contest = {}
    #create a dictionary for contests 0,1 where values are the luck values
    for l,c in contests:
        if c not in contest:
            contest[c]=[l]
        else:
            contest[c].append(l)
    
    result=0        
    if 0 in contest:
        result = sum(contest[0])
        
    if 1 in contest:
        s=sorted(contest[1],reverse=True)
        # only want to add the largest first k luck values from important contests
        result+=sum(s[:k])
        result -=sum(s[k:])
        
    return result
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    k = int(first_multiple_input[1])

    contests = []

    for _ in range(n):
        contests.append(list(map(int, input().rstrip().split())))

    result = luckBalance(k, contests)

    fptr.write(str(result) + '\n')

    fptr.close()
