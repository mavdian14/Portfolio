#!/bin/python3
import collections
import math
import os
import random
import re
import sys

def choose(n,k):
    if k>n:
        return 0
    k = min(k, n-k)
    num,den = 1,1 
    for i in range(k):
        num *= (n-i)
        den *= i+1
    return num//den

def squareCount(l):
    counter = collections.Counter(l)
    l = tuple(counter.keys())
    choose2 = collections.Counter()
    choose3 = collections.Counter()
    choose4 = collections.Counter()
    le = len(l)
    for n in counter:
        count = counter[n]
        if count >= 2:
            choose2[n] = choose(count,2)
            if count >= 3:
                choose3[n] = choose(count,3)
                if count>=4:
                    choose4[n] = choose(count,4)
    t1 = 0
    t2 = 0
    for i in range(le):
        if counter[2*l[i]] >= 2 and counter[l[i]] >= 4:
            t1 += choose4[l[i]]*choose2[2*l[i]]
        if counter[l[i]]>=2:
            for j in range(i+1,le):
                if counter[l[j]]>=2 and counter[l[i]+l[j]] >= 2:
                    t2 += choose2[l[i]]*choose2[l[j]]*choose2[l[i]+l[j]]
                    
    doubles = collections.Counter()
    for i in range(le):
        if counter[l[i]] >= 2 and counter[2*l[i]] >= 2:
            doubles[2*l[i]] = choose2[l[i]]
 
    pairs = collections.Counter()
    mpairs = collections.Counter()
    for i in range(le):
        for j in range(i+1,le):
            if counter[l[i]+l[j]] >= 2:
                pairs[l[i]+l[j]] += counter[l[i]]*counter[l[j]]
                mpairs[l[i]+l[j]] += counter[l[i]]**2*counter[l[j]]**2

    t3 = sum(pairs[s]*doubles[s]*choose2[s] for s in doubles if s in pairs)
    t4 = sum((pairs[s]**2 - mpairs[s])*choose2[s] for s in pairs)//2
    CD = collections.Counter()

    for d in range(le):
        if counter[l[d]]>=3:
            for c in range(le):
                if l[c] < l[d]:
                    CD[l[d]-l[c]] += choose3[l[d]]*counter[l[c]]

    s1 = 0
    s2 = 0
    s4 = 0
    
    for a in range(le):
        for b in range(a+1,le):
            s1 += 2*CD[l[a]+l[b]]*counter[l[a]]*counter[l[b]]
            if counter[l[a] + 2*l[b]] >= 3:
                s2 += 2*choose3[l[a] + 2*l[b]]*counter[l[a]]*counter[l[b]]**2
            if counter[2*l[a] + l[b]] >= 3:
                s2 += 2*choose3[2*l[a] + l[b]]*counter[l[b]]*counter[l[a]]**2
            if counter[l[b]] >= 2 and counter[l[a] + 2*l[b]] >= 3:
                s4 += counter[l[a]]*choose2[l[b]]*choose3[l[a]+2*l[b]]
            if counter[l[a]] >= 2 and counter[2*l[a] + l[b]] >= 3:
                s4 += counter[l[b]]*choose2[l[a]]*choose3[2*l[a]+l[b]]

    s = (s1 - s2)//6
    s3 = 0
    for a in range(le):
        if counter[l[a]] >= 3 and counter[3*l[a]]>=3:
            s3 += choose3[l[a]]*choose3[3*l[a]]
            
            
    return t1 + t2 + t3 + t4 + s + s3 + s4


if __name__ == '__main__':
    n = int(input())

    l = list(map(int, input().rstrip().split()))

    print(squareCount(l))
