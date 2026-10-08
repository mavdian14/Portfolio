#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'nimbleGame' function below.
#
# The function is expected to return a STRING.
# The function accepts INTEGER_ARRAY s as parameter.
#

def nimbleGame(s):
    r=0
    for i in range(len(s)):
        if s[i]%2==1:
            r ^=i
    
    # i.e. if r != 0
    if r:
        return "First"
    else:
        return "Second"

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        n = int(input().strip())

        s = list(map(int, input().rstrip().split()))

        result = nimbleGame(s)

        fptr.write(result + '\n')

    fptr.close()
