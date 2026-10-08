#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'getMax' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts STRING_ARRAY operations as parameter.
#

def getMax(operations):
    stack = [0]
    res = []
    for val in operations:
        #split the strings characters for each string in operations
        val=val.split()
        if val[0] == '1':
            stack.append(max(int(val[1]),stack[-1]))
        elif val[0] == '2':
            stack.pop()
        #print the element
        else:
            res.append((stack[-1]))
    
    return res
                    

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    ops = []

    for _ in range(n):
        ops_item = input()
        ops.append(ops_item)

    res = getMax(ops)

    fptr.write('\n'.join(map(str, res)))
    fptr.write('\n')

    fptr.close()
 
