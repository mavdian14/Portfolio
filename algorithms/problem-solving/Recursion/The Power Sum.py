#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'powerSum' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER X
#  2. INTEGER N
#
def power_sum_helper(total,power,num):
    power_num=num**power
    if power_num == total:
        return 1
    elif power_num > total:
        return 0
    else:
        return power_sum_helper(total,power,num+1) + power_sum_helper(total-power_num,power,num+1)
    
def powerSum(X, N):
    return power_sum_helper(X,N,1)
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    X = int(input().strip())

    N = int(input().strip())

    result = powerSum(X, N)

    fptr.write(str(result) + '\n')

    fptr.close()
