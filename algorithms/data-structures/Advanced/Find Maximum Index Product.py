#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'solve' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER_ARRAY arr as parameter.
#

def solve(arr):
    n = len(arr)
    if n < 3:
        return 0

    ipl =[]
    ipr = []
    left = []
    right =[]

    for i in range(n-2):
        al = 0
        dif = arr[i] - arr[i+1] 
        if dif > 0:
            left.append((dif,i+1))
            al = i+1
        elif dif == 0:
            if ipl:
                al = ipl[-1]          
        else:
            ii= len(left) -1
            while ii >= 0 and dif + left[ii][0] <= 0:
                ii -= 1
            if ii >= 0:
                al = left[ii][1]

        ipl.append(al)


        ar = 0
        dif = arr[n -1 -i] - arr[n -2 -i] 
        if dif > 0:
            right.append((dif,n -i))
            ar = n -i
        elif dif == 0:
            if ipr:
                ar = ipr[-1]
        else:
            ii=len(right) -1
            while ii >= 0 and dif + right[ii][0] <= 0:
                ii -= 1
            if ii >= 0:
                ar = right[ii][1]

        ipr.append(ar)

    ipr.reverse()        
    ip = list(map(lambda x, y: x * y ,ipl, ipr))
    return max(ip) 

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    arr_count = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    result = solve(arr)

    fptr.write(str(result) + '\n')

    fptr.close()
