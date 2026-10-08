#!/bin/python3

import math
import os
import random
import re
import sys

def calculate_median(a):
    mid1 = a[len(a) // 2]
    mid2 = a[(len(a) - 1) // 2]
    return (mid1 + mid2) / 2

def sort_insert(arr, num):
    if not arr:
        arr.append(num)
        return

    start = 0
    end = len(arr) -1
    while start < end:
        mid = (end + start) // 2
        if arr[mid] < num:
            start = mid + 1
        elif arr[mid] >= num:
            end = mid - 1
    else:
        if num < arr[start]:
            arr.insert(start, num)
        else:
            #.insert() inserts the given element at the given index
            arr.insert(start+1, num)

def runningMedian(a):
    arr = []
    result = []
    for i in range(len(a)):
        sort_insert(arr, a[i])
        result.append(calculate_median(arr))
    return result

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    a_count = int(input().strip())

    a = []

    for _ in range(a_count):
        a_item = int(input().strip())
        a.append(a_item)

    result = runningMedian(a)

    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
