#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'primeXor' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER_ARRAY a as parameter.
#
MAX=8192
MOD=10**9+7
from collections import Counter
prime=[True for i in range(MAX+1)]

def sieve():
    prime[0]=prime[1]=False
    for p in range(2,MAX+1):
        if prime[p]==True:
            for j in range(2*p,MAX+1,p):
                prime[j]=False

def primeXor(a):
    sieve()
    count=0
    c = Counter(a)
    M = 8192
    
    dp = [0] * M
    dp[0] = 1 
    range_M = range(M)
    
    for e in c.keys():
        even, odd = (c[e]//2 + 1), ((c[e] + 1)//2)
        dp = [(dp[i] * even + dp[i^e] * odd) % MOD for i in range_M]
        
    for j in range_M:
        if prime[j]:
            count += dp[j]
            if count > MOD:
                count %= MOD
    
    return count%MOD

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    q = int(input().strip())

    for q_itr in range(q):
        n = int(input().strip())

        a = list(map(int, input().rstrip().split()))

        result = primeXor(a)

        fptr.write(str(result) + '\n')

    fptr.close()
