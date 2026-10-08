#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'playWithWords' function below.
#
# The function is expected to return an INTEGER.
# The function accepts STRING s as parameter.
#

def playWithWords(s):
    n = len(s)
    memo = [[0] * n for _ in range(n)]
    for i in range(n):
        memo[i][i] = 1

    for length in range(2, n+1):
        for i in range(n-length+1):
            j = i+length-1
            if s[i] == s[j]:
                if length == 2:
                    memo[i][j] = 2
                else:
                    memo[i][j] = memo[i+1][j-1] + 2
            else:
                memo[i][j] = max(memo[i][j-1], memo[i+1][j])
    m = 0
    for i in range(n-1):
        m = max(m, memo[0][i] * memo[i+1][n-1])
    return m
                    

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    s = input()

    result = playWithWords(s)

    fptr.write(str(result) + '\n')

    fptr.close()
