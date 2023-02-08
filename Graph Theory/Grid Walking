#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'gridWalking' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER m
#  2. INTEGER_ARRAY x
#  3. INTEGER_ARRAY D
#

def gridWalking(m, x, D):
    #m = num of steps, x= an int arr where each x[i] is a coord in the ith dimension where 1<=i<=n, D=int arr where D[i] is the upper limit of the axis in the ith dimension
    MOD = 10 ** 9 + 7
    n = len(D)
    md = [[0 for _ in range(n + 1)] for _ in range(m + 1)]
    for i in range(n):
        M = [[0 for _ in range(m + 1)] for _ in range(D[i] + 1)]
        for j in range(1, D[i] + 1):
            M[j][0] = 1
        for j in range(1, m + 1):
            for k in range(1, D[i] + 1):
                M[k][j] = 0
                if k - 1 > 0:
                    M[k][j] = (M[k][j] + M[k - 1][j - 1]) % MOD;
                if k + 1 <= D[i]:
                    M[k][j] = (M[k][j] + M[k + 1][j - 1]) % MOD
        md[0][i + 1] = 1
        for j in range(1, m + 1):
            md[j][i + 1] = M[x[i]][j]
    c = [[0 for _ in range(m + 1)] for _ in range(m + 1)]
    for i in range(m + 1):
        c[i][0] = 1
        c[i][i] = 1
    for i in range(1, m + 1):
        for j in range(1, i):
            c[i][j] = (c[i - 1][j - 1] + c[i - 1][j]) % MOD
    mdt = [[0 for _ in range(n + 1)] for _ in range(m + 1)]
    for i in range(m + 1):
        mdt[i][1] = md[i][1]
    for i in range(n + 1):
        mdt[0][i] = 1
    for i in range(2, n + 1):
        for j in range(1, m + 1):
            mdt[j][i] = 0
            for k in range(j + 1):
                mdt[j][i] = (mdt[j][i] + ((c[j][j - k] * ((mdt[k][i - 1] * md[j - k][i]) % MOD)) % MOD)) % MOD
    return mdt[m][n]
            
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        first_multiple_input = input().rstrip().split()

        n = int(first_multiple_input[0])

        m = int(first_multiple_input[1])

        x = list(map(int, input().rstrip().split()))

        D = list(map(int, input().rstrip().split()))

        result = gridWalking(m, x, D)

        fptr.write(str(result) + '\n')

    fptr.close()
