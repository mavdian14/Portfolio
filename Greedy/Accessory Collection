#!/bin/python3

import os
import sys

def acessoryCollection(L, A, N, D):
    if D > A or N < D or N > L: return "SAD"
    elif D == 1: return str (L * A)
    else:
        max = 0
        a2Max = (N - 1) // (D - 1)
        for a2 in range (a2Max, 0, -1):
            a1 = N + (a2 - 1) - a2 * (D - 1)
            n = (L - a1) // a2
            a3 = (L - a1) % a2
            if n > A - 1 or n == A - 1 and a3 > 0: break
            sum = A * a1 + (A - 1 + A - n) * n // 2 * a2 + a3 * (A - n - 1)
            if sum <= max: break
            max = sum
        if max: return str (max)
        else: return "SAD"

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    T = int(input())

    for T_itr in range(T):
        LAND = input().split()

        L = int(LAND[0])

        A = int(LAND[1])

        N = int(LAND[2])

        D = int(LAND[3])

        result = acessoryCollection(L, A, N, D)

        fptr.write(result + '\n')

    fptr.close()
