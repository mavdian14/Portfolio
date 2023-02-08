#!/bin/python3

import math
import os
import random
import re
import sys

def andXorOr(a):
    #pA -the result of pairing a[-1] and popped
    #pStack-the result of pairing stack[-1] and popped
    stack=[a.pop()] 
    popped=a.pop()
    maxRes=pStack=pA= -1 
    while True: #
        #pairing and getting the result of the pairs:
        if stack:    
            pStack=stack[-1]^popped
        if a:
            pA=a[-1]^popped
        maxRes=max(maxRes,pA,pStack) #getting the max result so far
        if stack and stack[-1]>popped: 
            stack.pop() #
            continue
        elif not a:
            return maxRes
        elif not stack or stack[-1]<popped<a[-1]:
            stack.append(popped)
        elif stack[-1]<popped>a[-1]:
            pass
        popped=a.pop()

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    a_count = int(input().strip())

    a = list(map(int, input().rstrip().split()))

    result = andXorOr(a)

    fptr.write(str(result) + '\n')

    fptr.close()
