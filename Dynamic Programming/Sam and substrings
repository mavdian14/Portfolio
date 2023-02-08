#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'substrings' function below.
#
# The function is expected to return an INTEGER.
# The function accepts STRING n as parameter.
#

def substrings(n):
    leen = len(n)
    ans = 0
    mod = 10**9+7
    i = 0
    for ltt in n[::-1]:
        i = (10*(i%mod)+1)%mod
        lt = int(ltt)
        ans+=(lt*i*leen)%mod
        leen-=1
    return ans%mod
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = input()

    result = substrings(n)

    fptr.write(str(result) + '\n')

    fptr.close()
