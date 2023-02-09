#!/bin/python3

import math
import os
import random
import re
import sys

n,q = [int(number) for number in input().split()]

mylist = [int(number) for number in input().split()]

for step in range(q):
    minmax = 0
    d = int(input())
    maxnumber = 0
    for i in range(n):
        if mylist[i] >= maxnumber:
            maxnumber = mylist[i]
        elif i >= d:
            if mylist[i-d] == maxnumber:
                maxnumber = max(mylist[i-d+1:i+1])
        if i >= d-1:
            if minmax == 0 or minmax > maxnumber:
                minmax = maxnumber

    print(minmax)
