#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'stockmax' function below.
#
# The function is expected to return a LONG_INTEGER.
# The function accepts INTEGER_ARRAY prices as parameter.
#

def stockmax(prices):
    m = prices.index(max(prices))
    if m == len(prices)-1:
        r = (-1)*sum(prices[:m])+prices[m]*(len(prices)-1)
    elif m == 0:
        r = stockmax(prices[m+1:])
    else:
        r = (stockmax(prices[:m+1])) + (stockmax(prices[m+1:]))
    
    return r

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        n = int(input().strip())

        prices = list(map(int, input().rstrip().split()))

        result = stockmax(prices)

        fptr.write(str(result) + '\n')

    fptr.close()
