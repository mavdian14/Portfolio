#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'insertionSort2' function below.
#
# The function accepts following parameters:
#  1. INTEGER n
#  2. INTEGER_ARRAY arr
#
def insertionsort1(start,arr):
    probe = arr[start]
    for i in range(start-1,-1,-1):
        if arr[i] > probe:
            arr[i+1]=arr[i]
        else:
            arr[i+1]=probe
            break
    if arr[0] > probe:
        arr[0] = probe
def insertionSort2(n, arr):
    for i in range(1,len(arr)):
        insertionsort1(i,arr)
        print(" ".join(map(str,arr)))
    

if __name__ == '__main__':
    n = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    insertionSort2(n, arr)
