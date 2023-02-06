#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'cutTheSticks' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts INTEGER_ARRAY arr as parameter.
#

def cutTheSticks(arr):
    res = []
    while arr:
        res.append(len(arr))
        arr_min =min(arr)
        #for each entry in arr, reduce its value by arr_min, the map() func allows us to run function lambda on all the elements in the list
        arr = list(map(lambda x: x-arr_min, arr))
        #for each entry x <= 0 remove it from arr (essentially removing the shortest sticks)
        arr=list(filter(lambda x: x > 0,arr))
    return res

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    result = cutTheSticks(arr)

    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
