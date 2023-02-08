#!/bin/python3

import math
import os
import random
import re
import sys

nimbers = dict()
def findNimber(x,y):
    if x<1 or y<1 or x>15 or y>15:
        return -1
    if (x,y) in nimbers:
        return nimbers[(x,y)]
    check = []
    check.append(findNimber(x-1,y-2))
    check.append(findNimber(x+1,y-2))
    check.append(findNimber(x-2,y+1))
    check.append(findNimber(x-2,y-1))
    i=0
    while True:
        if i not in check:
            nimbers[(x,y)]=i
            return i
        i+=1

def chessboardGame(coins):
    grundy=0
    for x,y in coins:
        grundy ^= findNimber(x,y)
    return "First" if grundy else "Second"

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    
    t=int(input())
    for t_itr in range(t):
        k = int(input())
        
        coins = []
        
        for _ in range(k):
            coins.append(list(map(int,input().rstrip().split())))
        result = chessboardGame(coins)
        
        fptr.write(result + '\n')
    
    fptr.close()
