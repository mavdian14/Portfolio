#!/bin/python3

import math
import os
import random
import re
import sys


def kFactorization(n, A):
    if (n == 1):
        return [1]
    
    A = sorted(A, reverse=True)
    
    if (len(A) == 1) and (A[0] == 1):
        return A
    
    if A[-1] == 1:
        A.pop()
    
    divisors = []
    wasHit = True
    sizeA = len(A)
    while(n > 1) and (wasHit):
        wasHit = False
        i = 0
        while(i < sizeA):
            if (n % A[i] == 0):
                wasHit = True
                divisors.append(A[i])
                n = n // A[i]
            i += 1
    if (n > 1):
        return [-1]

    divisors.sort()
    results = [1]
    for divisor in divisors:
        n *= divisor
        results.append(n)

    return results

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    k = int(first_multiple_input[1])

    A = list(map(int, input().rstrip().split()))

    result = kFactorization(n, A)

    fptr.write(' '.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
