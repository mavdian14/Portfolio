#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'legoBlocks' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER n
#  2. INTEGER m
#

def legoBlocks(n, m):
    MOD = 10**9 + 7
    #find the # of combinations
    #Base case: w=0 => combo=1, w=1 => combo=1, w=2 => combo=2, w=3 => combo=4
    row_combinations = [1,1,2,4]
    #build row combos up to current wall's width
    while len(row_combinations) <= m:
        row_combinations.append(sum(row_combinations[-4:])%MOD)
    
    #find total combinations
    total = [pow(c,n,MOD) for c in row_combinations]
    #find total unstable configs
    unstable = [0,0]
    
    #break wall into left & right part, calc each combo. From width of 2, we consider violations
    for i in range(2,m+1):
        #i: current total width, j:left width, i-j: right width, f:(left part - prev vertical violation)*right part
        f= lambda j: (total[j]-unstable[j])*total[i-j]
        result = sum(map(f,range(1,i)))
        unstable.append(result%MOD)
    
    #Print total stable wall combos
    return (total[m]-unstable[m])%MOD

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        first_multiple_input = input().rstrip().split()

        n = int(first_multiple_input[0])

        m = int(first_multiple_input[1])

        result = legoBlocks(n, m)

        fptr.write(str(result) + '\n')

    fptr.close()
