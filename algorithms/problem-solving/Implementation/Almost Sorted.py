#!/bin/python3

import math
import os
import random
import re
import sys
#used to duplicate the array
from copy import *
#
# Complete the 'almostSorted' function below.
#
# The function accepts INTEGER_ARRAY arr as parameter.
#

def almostSorted(arr):
    sortarr = deepcopy(arr)  #copy array elements
    sortarr.sort()
    
    # if the array is already sorted
    if sortarr == arr:
        print("yes")
        return
    
    #if the array can be sorted
    l = r = -1
    
    #left index loop
    for i in range(n-1):
        if arr[i] > arr[i+1]:
            l = i
            break
    
    #right index loop
    for i in range(n-1,0,-1):
        if arr[i] < arr[i-1]:
            r = i
            break
    
    # check for swap
    temp = deepcopy(arr)
    
    #swap
    temp[l],temp[r] = temp[r],temp[l]
    
    if temp == sortarr:
        print("yes")
        print("swap", l+1,r+1)
        return
    
    #check for reverse
    temp = deepcopy(arr)
    temp = temp[:l] + temp[l:r+1][::-1] + temp[r+1:]
    if temp == sortarr:
        print("yes")
        print("reverse",l+1,r+1)
        return
    
    print("no")
        
if __name__ == '__main__':
    n = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    almostSorted(arr)
