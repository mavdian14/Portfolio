#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'equal' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER_ARRAY arr as parameter.
#

def equal(arr):
    arr.sort()
    #arr if we give everyone 1 piece
    arr2 = [x+1 for x in arr]
    arr2[0] = arr[0]
    arr3 = [x+2 for x in arr]
    arr3[0] = arr[0]
    
    def test(arr):
        cost = 0
        steps = 0
        cur = arr[0]
        for i in range(1,len(arr)):
            diff = abs(arr[i]+cost-cur)
            cur = max(cur,arr[i]+cost)
            cost+=diff
            steps+=diff//5+(diff%5)//2+(diff%5)%2
        return steps
    return min(test(arr),test(arr2)+1,test(arr3)+1)
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        n = int(input().strip())

        arr = list(map(int, input().rstrip().split()))

        result = equal(arr)

        fptr.write(str(result) + '\n')

    fptr.close()
