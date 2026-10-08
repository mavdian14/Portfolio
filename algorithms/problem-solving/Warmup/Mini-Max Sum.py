#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'miniMaxSum' function below.
#
# The function accepts INTEGER_ARRAY arr as parameter.
#

def miniMaxSum(arr):
    #sort the array in ascending order
    arr=sorted(arr)
    #print sum of first 4 ints, then last 4 ints
    print(sum(arr[:-1]),sum(arr[1:]))

if __name__ == '__main__':

    arr = list(map(int, input().rstrip().split()))

    miniMaxSum(arr)
