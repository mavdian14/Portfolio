#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'minimumLoss' function below.
#
# The function is expected to return an INTEGER.
# The function accepts LONG_INTEGER_ARRAY price as parameter.
#

def minimumLoss(price):
    d = {}
    #enumerate() converts price into an enumerate object, which contains counters as keys
    for i,p in enumerate(price):
        d[p] = i
    
    price.sort()
    
    min_value = sys.maxsize
    
    for i in range(1,len(price)):
        if d[price[i-1]] > d[price[i]]:
            min_value = min(min_value, price[i]-price[i-1])
    
    return min_value
        

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    price = list(map(int, input().rstrip().split()))

    result = minimumLoss(price)

    fptr.write(str(result) + '\n')

    fptr.close()
