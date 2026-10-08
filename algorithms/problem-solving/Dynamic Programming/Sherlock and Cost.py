#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'cost' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER_ARRAY B as parameter.
#

def cost(B):
    a=b=0
    for i in range(1,len(B)):
        new_a=max((abs(B[i]-B[i-1])+a),(abs(B[i]-1)+b))
        new_b=max((abs(1-B[i-1])+a),b)
        a=new_a
        b=new_b
    return max(a,b)
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        n = int(input().strip())

        B = list(map(int, input().rstrip().split()))

        result = cost(B)

        fptr.write(str(result) + '\n')

    fptr.close()
