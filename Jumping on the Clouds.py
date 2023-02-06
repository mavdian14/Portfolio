#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'jumpingOnClouds' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER_ARRAY c as parameter.
#

def jumpingOnClouds(c):
    res=0
    ind=0
    #iterate until reach the end of cloud path
    while ind != len(c)-1:
        if ind != len(c)-2 and c[ind+2] ==0:
            ind+=2
        else:
            ind+=1
        res+=1
    return res
        #you should always jump 2 clouds if that cloud is safe or not the 2nd last cloud, otherwise jump 1 cloud

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    c = list(map(int, input().rstrip().split()))

    result = jumpingOnClouds(c)

    fptr.write(str(result) + '\n')

    fptr.close()
