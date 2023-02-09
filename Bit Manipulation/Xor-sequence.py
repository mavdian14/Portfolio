#!/bin/python3

import math
import os
import random
import re
import sys

# Complete the xorSequence function below.
def xorSequence(l, r):
    def G(x):
        m=x%4
        if m==0:
            return x
        elif m==1:
            return 1
        elif m==2:
            return x+1
        elif m==3:
            return 0
    
    pos=l
    result=0
    
    while True:
        if pos%8==0:
            break
        else:
            result^=G(pos)
            pos+=1
    
    pos=r
    while True:
        if pos%8==0:
            result^=G(pos)
            break
        else:
            result^=G(pos)
            pos-=1
    
    return result

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    q = int(input())

    for q_itr in range(q):
        lr = input().split()

        l = int(lr[0])

        r = int(lr[1])

        result = xorSequence(l, r)

        fptr.write(str(result) + '\n')

    fptr.close()
