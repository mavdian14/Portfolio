#!/bin/python3

import math
import os
import random
import re
import sys

class fenpiece:
    __slots__ = ['x','p','px','c']
    def __init__(self,x=0,p=0,px=0,c=0):
        self.x = x
        self.p = p
        self.px = px
        self.c = c
    def __iadd__(self,other):
        self.x += other.x
        self.p += other.p
        self.px += other.px
        self.c += other.c
        return self
    def __radd__(self,other):
        return fenpiece(self.x,self.p,self.px,self.c)
    def __sub__(self,other):
        return fenpiece(self.x-other.x,self.p-other.p,self.px-other.px,self.c-other.c)
        
def fensum(seq,i):
    sum = 0
    while i:
        sum += seq[i-1]
        i -= i&-i
    return sum

def fensumrange(seq,i,j):
    return fensum(seq,j) - fensum(seq,i)

def fenadd(seq,i,v):
    i += 1
    bound = len(seq) + 1
    while i < bound:
        seq[i-1] += v
        i += i&-i
        
pBound = 10001
magicmod = 1000000007
fenlist = [fenpiece() for i in range(pBound)]
T = int(input())
for t in range(T):
    total = 0
    N = int(input())
    X = [int(s) for s in input().split()]
    P = [int(s) for s in input().split()]
    cities = sorted(zip(X,P))
    cable = 0
    for x,p in cities:
        underP = fensum(fenlist,p)
        overP = fensumrange(fenlist,p,pBound)
        cable =  (cable + p*(underP.c*x - underP.x) + overP.p*x - overP.px)%magicmod
        fenadd(fenlist,p,fenpiece(x,p,x*p,1))
    print(cable)
    for f in fenlist:f.__init__()
