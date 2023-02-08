#!/bin/python3

import math
import os
import random
import re
import sys
from functools import reduce

def towerBreakers(arr):
    return nim(list(map(setupnim,arr)))
def nim(pile):
    print(pile)
    return 1 if reduce(lambda x,y: x^y, pile) else 2

def setupnim(n):
    i=2
    t=0
    if n%2==0: t+=1
    while i*i<=n:
        while n%i==0:
            if n%2==1: t+=1
            n=n/i
        i+=1
    if n>1 and n%2==1: t+=1
    return t

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input())

    for t_itr in range(t):
        arr_count = int(input())

        arr = list(map(int, input().rstrip().split()))

        result = towerBreakers(arr)

        fptr.write(str(result) + '\n')

    fptr.close()
