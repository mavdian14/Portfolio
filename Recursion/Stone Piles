#!/bin/python3

import math
import os
import random
import re
import sys

def mex(l):
    l = sorted(set(l))
    for i,x in enumerate(l):
        if i != x:
            return i
    return len(l)

def sg(n, sg_cache=None):
    #print("sg",n,sg_cache)
    if n <= 2:
        return 0
    if sg_cache and not (sg_cache[n] is None):
        #print("cached",n,sg_cache[n])
        return sg_cache[n]
    def successors(m, beg):
        l = []
        for i in range(beg+1,(1+m)//2):
            sgi = sg(i, sg_cache)
            l.append(sgi ^ sg(m-i, sg_cache))
            for j in successors(m-i, i):
                l.append(sgi ^ j)
        return l
    ret = mex(successors(n, 0))
    sg_cache[n] = ret
    #print("computed",n,ret)
    return ret

def sgl(l):
    sg_cache = [0,0,0]+[None]*(max(l)-2)
    ret = 0
    for n in l:
        ret ^= sg(n, sg_cache)
    return ret, sg_cache

def stonePiles(l):
    return ["BOB","ALICE"][sgl(l)[0] != 0]

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input())

    for t_itr in range(t):
        arr_count = int(input())

        arr = list(map(int, input().rstrip().split()))

        result = stonePiles(arr)

        fptr.write(result + '\n')

    fptr.close()
