#!/bin/python3

import math
import os
import random
import re
import sys

def isP(n):
    if n<=3:
        return True
    if ((n%2==0)|(n%3==0)):
        return False
    for d in range(5,int(n**.5)+1,6):
        if ((n%d==0)|(n%(d+2)==0)):
            return False
    return True

def getP(m):
    P=[1,2]
    for n in range(3,m+1,2):
        if isP(n):
            P.append(n)
    return P            

P=getP(int(10**5+1000))

g = int(input().strip())
for a0 in range(g):
    n = int(input().strip())
    for i in range(len(P)):
        if P[i]>n:
            c=i-1
            break
    if c%2==1:
        print("Alice")
    else:
        print("Bob")
