#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'dynamicArray' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts following parameters:
#  1. INTEGER n
#  2. 2D_INTEGER_ARRAY queries
#

def dynamicArray(n, queries):
    #initialization all the nested lists
    seq = [[] for _ in range(n)]
    lastanswer = 0
    result = []
    
    #main logic: query operation
    #q: # of queries, 
    for q,x,y in queries:
        if q == 1:
            #find index of seq
            idx = (x ^ lastanswer)%n
            seq[idx].append(y)
        else:
            idx = (x ^ lastanswer)%n
            v = y%len(seq[idx])
            lastanswer = seq[idx][v]
            result.append(lastanswer)
            
    return result

    return result
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    q = int(first_multiple_input[1])

    queries = []

    for _ in range(q):
        queries.append(list(map(int, input().rstrip().split())))

    result = dynamicArray(n, queries)

    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
