#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'countSort' function below.
#
# The function accepts 2D_STRING_ARRAY arr as parameter.
#

def countSort(arr):
    #100 is the constraint of num elements
    result = [[] for i in range(100)]
    
    #first half of iteration
    for i in range(n//2):
        result[int(arr[i][0])].append('-')
        
    #2nd half of iteration
    for i in range(n//2,n):
        result[int(arr[i][0])].append(arr[i][1])
        
    #print the results
    for string in result:
        #condition to test the arr is non-empty
        if string:
            print(*string, end=' ')

if __name__ == '__main__':
    n = int(input().strip())

    arr = []

    for _ in range(n):
        arr.append(input().rstrip().split())

    countSort(arr)
