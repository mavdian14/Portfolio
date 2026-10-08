#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'twoStacks' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER maxSum
#  2. INTEGER_ARRAY a
#  3. INTEGER_ARRAY b
#

def twoStacks(x, a, b):
    maxnum = total  = i = j = 0
    #take as many elements as possible from stack a
    while i < len(a) and total + a[i] <= x:
        total += a[i]
        i+=1
        maxnum +=1
    
    #take as many elements as possible from stack b
    while j < len(b) and i>=0:
        total += b[j]
        j+=1
        #remove taken element from stack A
        while i > 0 and total > x:
            i-=1
            total -= a[i]
        
        #check for condition maxnum & update
        if total <=x and maxnum < i+j:
            maxnum = i+j
    
    return maxnum
    
        

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    g = int(input().strip())

    for g_itr in range(g):
        first_multiple_input = input().rstrip().split()

        n = int(first_multiple_input[0])

        m = int(first_multiple_input[1])

        maxSum = int(first_multiple_input[2])

        a = list(map(int, input().rstrip().split()))

        b = list(map(int, input().rstrip().split()))

        result = twoStacks(maxSum, a, b)

        fptr.write(str(result) + '\n')

    fptr.close()
