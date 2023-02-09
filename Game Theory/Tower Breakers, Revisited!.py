#!/bin/python3

import math
import os
import random
import re
import sys

from functools import reduce
from operator import xor

def towerBreakers(arr):
    arr = map(factorcount,arr)
    return 1 if reduce(xor,arr) else 2

PRIMES = None

def factorcount(n:int) -> int:
    if not PRIMES: init_primes()
    prime_it = iter(PRIMES)
    result = 0
    while ...:
        p = next(prime_it)
        if p*p > n: break
        while n%p == 0:
            result += 1
            n //= p
    if n > 1: result += 1
    return result

def init_primes():
    global PRIMES
    PRIMES = [2,3,5,7]
    for p in range(10,1100):
        if factorcount(p) == 1:
            PRIMES.append(p)

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        arr_count = int(input().strip())

        arr = list(map(int, input().rstrip().split()))

        result = towerBreakers(arr)

        fptr.write(str(result) + '\n')

    fptr.close()
