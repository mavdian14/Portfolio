#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'sumXor' function below.
#
# The function is expected to return a LONG_INTEGER.
# The function accepts LONG_INTEGER n as parameter.

#n&1 - return 1 if if the least significant bit of n is 1, otherwise returns 0

#x>>=1  - "Set x to itself shifted by one bit to the right. essentially it evaluates the new value of x after the shift"

def sumXor(n):
    result = 1
    while n:
        b = n&1 #checks if odd or even (bitwise AND)
        n>>=1 # divide by 2 (bitwise left shift by 1)
        if b ==0:
            result *=2
    return result
            

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    result = sumXor(n)

    fptr.write(str(result) + '\n')

    fptr.close()
