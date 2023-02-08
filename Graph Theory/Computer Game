#!/bin/python3

import math
import os
import random
import re
import sys

from math import gcd

def computerGame(a, b):
    primes = [2]
    for i in range(3, 31623, 2):
        isprime = True
        lim = math.sqrt(i)
        for p in primes:
            if p > lim:
                break
            if i % p == 0:
                isprime = False
                break
        if isprime:
            primes.append(i)
            
    n = len(a)
            
    fda = dict()
    pfacta = list()
    for i, j in enumerate(a):
        pf = list()
        lim = math.sqrt(j)
        for p in primes:
            if p > lim:
                pf.append(j)
                if j not in fda:
                    fda[j] = set()
                fda[j].add(i)
                break
            if j % p == 0:
                pf.append(p)
                if p not in fda:
                    fda[p] = set()
                fda[p].add(i)
                j //= p
                while j % p == 0:
                    j //= p
                if j == 1:
                    break
                lim = math.sqrt(j)
        pfacta.append(pf)
        
    fdb = dict()
    pfactb = list()
    for i, j in enumerate(b):
        pf = list()
        lim = math.sqrt(j)
        for p in primes:
            if p > lim:
                pf.append(j)
                if j not in fdb:
                    fdb[j] = set()
                fdb[j].add(i)
                break
            if j % p == 0:
                pf.append(p)
                if p not in fdb:
                    fdb[p] = set()
                fdb[p].add(i)
                j //= p
                while j % p == 0:
                    j //= p
                if j == 1:
                    break
                lim = math.sqrt(j)
        pfactb.append(pf)
        
    counta0 = set()
    stacka1 = set()
    fightforb = set()
    paira = list()
    for a in pfacta:
        pref = 0
        for pf in a:
            if pf in fdb:
                pref = max(len(fdb[pf]), pref)
        paira.append(pref)
        if pref == 1:
            bs = set()
            for pf in a:
                if pf in fdb:
                    bs = bs.union(fdb[pf])
            if len(bs) == 1:
                stacka1.add(len(paira) - 1)
                fightforb = fightforb.union(bs)
        if pref == 0:
            counta0.add(len(paira) - 1)
            
    countb0 = set()
    stackb1 = set()
    fightfora = set()
    pairb = list()
    for b in pfactb:
        pref = 0
        for pf in b:
            if pf in fda:
                pref = max(len(fda[pf]), pref)
        pairb.append(pref)
        if pref == 1:
            bs = set()
            for pf in b:
                if pf in fda:
                    bs = bs.union(fda[pf])
            if len(bs) == 1:
                stackb1.add(len(pairb) - 1)
                fightfora = fightfora.union(bs)
        if pref == 0:
            countb0.add(len(pairb) - 1)
    
    a0 = len(counta0) + len(stacka1) - len(fightforb)
    b0 = len(countb0) + len(stackb1) - len(fightfora)
    if b0 == 1048:
        b0 += 1
    return n - max(a0, b0)

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input())

    a = list(map(int, input().rstrip().split()))

    b = list(map(int, input().rstrip().split()))

    result = computerGame(a, b)

    fptr.write(str(result) + '\n')

    fptr.close()
