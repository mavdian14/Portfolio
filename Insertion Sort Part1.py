#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'insertionSort1' function below.
#
# The function accepts following parameters:
#  1. INTEGER n
#  2. INTEGER_ARRAY arr
#

def insertionSort1(n, arr):
    #t is the last item in the array
    t=arr[n-1]
    #k is the 2nd last item in the array
    k=n-2
    # as sort is from right to left
    while k >=0 and t < arr[k]:
        arr[k+1]=arr[k]
        s=str(arr)[1:-1].replace(",","")
        print(s)
        k-=1
    arr[k+1]=t
    s=str(arr)[1:-1].replace(",", "")
    print(s)
     
    

if __name__ == '__main__':
    n = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    insertionSort1(n, arr)
