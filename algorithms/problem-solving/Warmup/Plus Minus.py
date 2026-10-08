#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'plusMinus' function below.
#
# The function accepts INTEGER_ARRAY arr as parameter.
#

def plusMinus(arr):  
    pos = 0
    zero = 0
    neg = 0
    for i in range(len(arr)):
        if arr[i] > 0:
            pos += 1
        elif arr[i] < 0:
            neg += 1
        else:
            zero +=1
    print(pos/len(arr))
    print(neg/len(arr))
    print(zero/len(arr))

if __name__ == '__main__':
    n = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    plusMinus(arr)
