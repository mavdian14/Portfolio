#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'towerBreakers' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER n
#  2. INTEGER m
#

def towerBreakers(n, m):
    while n >1 and m>1:
    
        if n%2==0 and m%2==0:
            return 2
        elif n%2==0 and m%2!=0:
            return 2
        elif n%2!=0 and m%2==0:
            return 1
        elif n%2!=0 and m%2!=0:
            return 1 
    else: 
        if n==1: 
            return 1
        else:
            return 2
            
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        first_multiple_input = input().rstrip().split()

        n = int(first_multiple_input[0])

        m = int(first_multiple_input[1])

        result = towerBreakers(n, m)

        fptr.write(str(result) + '\n')

    fptr.close()
