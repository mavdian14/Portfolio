#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'twoSubsequences' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER_ARRAY x
#  2. INTEGER r
#  3. INTEGER s
#

def twoSubsequences(x, r, s):
    #x is an array, r = sum(A), s =sum(B), ord(A)==ord(B)
    m = len(x)
    MOD = (10**9)+7
    h,l = (r+s) // 2, (r-s) // 2
    result = 0
    dp = [[0 for i in range(m+1)]for j in range(h+1)]
    dp[0][0]=1
    if x[0] <= h:
        dp[x[0]][1] =1
    for i in range(1,m):
        for k in range(1,m+1):
            dp[0][k] = 0
        for j in range(h,0,-1):
            dp[j][0] = 0
            for k in range(1,m+1):
                if j < x[i]:
                    dp[j][k] = dp[j][k]
                else:
                    dp[j][k] = (dp[j - x[i]][k-1] + dp[j][k])%MOD
    if l >= 0 and (r+s)%2 != 1 and (r-s)%2 != 1 and r!=0:
        for i in range(m):
            result = (result + (dp[h][i]*dp[l][i]))%MOD
    return result

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    m = int(first_multiple_input[0])

    r = int(first_multiple_input[1])

    s = int(first_multiple_input[2])

    x = list(map(int, input().rstrip().split()))

    result = twoSubsequences(x, r, s)

    fptr.write(str(result) + '\n')

    fptr.close()
