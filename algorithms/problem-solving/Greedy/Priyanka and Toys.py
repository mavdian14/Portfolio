#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'toys' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER_ARRAY w as parameter.
#

def toys(w):
    w.sort()
    containers =0
    max_weight=w[0]+4
    
    for weight in w:
        if weight <= max_weight:
            continue
        containers+=1
        max_weight = weight+4
    #add for last container
    containers+=1
    
    return containers


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    w = list(map(int, input().rstrip().split()))

    result = toys(w)

    fptr.write(str(result) + '\n')

    fptr.close()
