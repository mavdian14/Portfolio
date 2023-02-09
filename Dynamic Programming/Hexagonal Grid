#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'hexagonalGrid' function below.
#
# The function is expected to return a STRING.
# The function accepts following parameters:
#  1. STRING a
#  2. STRING b
#

def hexagonalGrid(a, b):
    if ((a.count('1') + b.count('1')) % 2 != 0):
        return 'NO'
    white = 0
    block = False
    for i in range(len(a)):
        if (a[i] == '1'):
            if block and white % 2 != 0:
                return 'NO'
            block = True
        elif (a[i] == '0'):
            block = False
            white += 1
        if (b[i] == '1'):
            if block and white % 2 != 0:
                return 'NO'
            block = True
        elif (b[i] == '0'):
            block = False
            white += 1          
    return 'YES'
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        n = int(input().strip())

        a = input()

        b = input()

        result = hexagonalGrid(a, b)

        fptr.write(result + '\n')

    fptr.close()
