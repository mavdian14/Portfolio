#!/bin/python3

import math
import os
import random
import re
import sys

M=1000000007
tests = int(input().strip())
for i in range(0,tests):
    n = int(input().strip())
    a = [int(x.strip()) for x in input().strip().split()]
    b0 = [0 for y in range(0,32)]
    b1 = [0 for y in range(0,32)]
    for k in range(0,n):        
        for j in range(0,32):
            if(a[k] & (1<<j)):
                tmp = b1[j]
                b1[j]=(b1[j]+1+b0[j])%M
                b0[j]=(b0[j]+tmp)%M
            else:
                b1[j]=(b1[j]+b1[j])%M
                b0[j]=(1+b0[j]+b0[j])%M
        

    cum = 0
    for j in range(0,32):
        val = ((1<<j)*b1[j])%M
        cum=(cum+val)%M

    print(cum)
