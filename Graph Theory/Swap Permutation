#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'swapPermutation' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts following parameters:
#  1. INTEGER n
#  2. INTEGER k
#

def swapPermutation(n, k):
    mod = 1000000007
    s = [1] + [0] * k
    t = [1] + [0] * k
    for i in range(1, n):
        temp = sum(s[max(k - i, 0):k]) % mod
        for j in range(k, 0, -1):
            s[j] = (s[j] + temp) % mod
            if j > i:
                temp = (temp + s[j - i - 1] - s[j - 1]) % mod
            else:
                temp = (temp - s[j - 1]) % mod
        for j in range(k, 0, -1):
            t[j] = (t[j] + i * t[j - 1]) % mod
    return sum(s[k % 2::2]) % mod, sum(t) % mod


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    nk = input().split()

    n = int(nk[0])

    k = int(nk[1])

    result = swapPermutation(n, k)

    fptr.write(' '.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
