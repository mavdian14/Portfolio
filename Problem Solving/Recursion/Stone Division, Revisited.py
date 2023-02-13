#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'stoneDivision' function below.
#
# The function is expected to return a LONG_INTEGER.
# The function accepts following parameters:
#  1. LONG_INTEGER n
#  2. LONG_INTEGER_ARRAY s
#
import collections
def stoneDivision(n, s):
    dp = collections.defaultdict(lambda: None)
    dp[1]=0
    def find(x):
        if dp[x] is None:
            mxx=0
            for i in s:
                if x!=i and x%i==0:
                    mx=1+(x//i)*find(i)
                    mxx=max(mxx,mx)
            dp[x]=mxx
        return dp[x]
    return find(n)

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    q = int(input().strip())

    for q_itr in range(q):
        first_multiple_input = input().rstrip().split()

        n = int(first_multiple_input[0])

        m = int(first_multiple_input[1])

        s = list(map(int, input().rstrip().split()))

        result = stoneDivision(n, s)

        fptr.write(str(result) + '\n')

    fptr.close()
