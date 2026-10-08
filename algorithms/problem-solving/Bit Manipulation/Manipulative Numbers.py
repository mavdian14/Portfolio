#!/bin/python3

import math
import os
import random
import re
import sys
import collections

def naive_solver(arr):
    for k in range(100):
        ctr = collections.Counter([num >> k for num in arr])
        print(type(ctr))
        for elem in ctr:
            if ctr[elem] * 2 > len(arr):
                return k-1
        
def manipulativeNumbers(a):
    return naive_solver(a)

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    a_count = int(input())

    a = list(map(int, input().rstrip().split()))

    result = manipulativeNumbers(a)

    fptr.write(str(result) + '\n')

    fptr.close()
