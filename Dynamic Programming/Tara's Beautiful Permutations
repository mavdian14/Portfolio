#!/bin/python3

import math
import os
import random
import re
import sys

factorial=[1,]
for i in range(1,2001):
    factorial.append(factorial[-1]*i)

pascal=[[0 for y in range(1001)] for x in range(1001)]

for i in range(1001):
    pascal[i][0]=1
    for j in range(1,i+1):
        pascal[i][j]=pascal[i-1][j-1]+pascal[i-1][j]
        
#print(factorial)
        
for _ in range(int(input())):
    m=int(input())
    n=len(set(input().split()))
    k=m-n
    
    ans=0
    f=1
    for j in range(0,k+1):

        kCj=pascal[k][j]
        ans+=f*kCj*factorial[m-j]//(2**(k-j))
        f=f*-1
    print(ans%1000000007)
