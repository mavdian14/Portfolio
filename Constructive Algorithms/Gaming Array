#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'gamingArray' function below.
#
# The function is expected to return a STRING.
# The function accepts INTEGER_ARRAY arr as parameter.
#

def gamingArray(arr):
    item=[]
    d=0
    for i in range(len(arr)):
        item.append([arr[i],i])
    item=sorted(item,key=lambda x: x[0],reverse=True)
    for i in item:
        try:
            arr[i[1]]=i[0]
            arr[i[1]:]=[]
            d+=1
        except: pass
    return 'ANDY' if d%2==0 else 'BOB'

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    g = int(input().strip())

    for g_itr in range(g):
        arr_count = int(input().strip())

        arr = list(map(int, input().rstrip().split()))

        result = gamingArray(arr)

        fptr.write(result + '\n')

    fptr.close()
