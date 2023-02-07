#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'jimOrders' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts 2D_INTEGER_ARRAY orders as parameter.
#

def jimOrders(orders):
    d = {}
    for i in range(len(orders)):
        serve_time = sum(orders[i])
        if serve_time not in d:
            d[serve_time] = [i+1]
        else:
            d[serve_time].append(i+1)
        
    result = []
    for serve_time in sorted(d.keys()):
        result.extend(d[serve_time])
    
    return result
        
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    orders = []

    for _ in range(n):
        orders.append(list(map(int, input().rstrip().split())))

    result = jimOrders(orders)

    fptr.write(' '.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
