#!/bin/python3

import math
import os
import random
import re
import sys

def f(k):
    if gf[k]>=0:
        return gf[k]
    res=ga[k]*gb[k]
    if res==0:
        gf[k]=0
        return 0
    for i in range(k+k,m+1,k):
        res-=f(i)
    gf[k]=res
    return res

if __name__ == '__main__':
    nmq = input().split()

    n = int(nmq[0])

    m = int(nmq[1])

    q = int(nmq[2])

    a = list(map(int, input().rstrip().split()))

    b = list(map(int, input().rstrip().split()))

    for q_itr in range(q):
        r1C1R2C2 = input().split()

        r1 = int(r1C1R2C2[0])

        c1 = int(r1C1R2C2[1])

        r2 = int(r1C1R2C2[2])

        c2 = int(r1C1R2C2[3])

        # Write Your Code Here
        sa=set(a[r1:r2+1])
        sb=set(b[c1:c2+1])
        na=len(a)
        nb=len(b)
        mxa=max(sa)
        mxb=max(sb)
        m=min(mxa,mxb)
        mm=max(mxa,mxb)

        ga=[0]*(m+1)
        gb=[0]*(m+1)
        ga[1]=na
        gb[1]=nb

        for i in range(2,m+1):
            for j in range(i,mm+1,i):
                if j in sa:
                    ga[i]+=1
                if j in sb:
                    gb[i]+=1
        gf=[-1]*(m+1)

        f(1)
        r=sum([(x>0) for x in gf])
        print(r)
