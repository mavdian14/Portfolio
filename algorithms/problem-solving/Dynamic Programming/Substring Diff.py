#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'substringDiff' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER k
#  2. STRING s1
#  3. STRING s2
#

def substringDiff(k, s1, s2):
    s1="*"+s1
    s2="*"+s2
    maxim=0
    matt=[[0 for _ in range(len(s1))]for o in range(len(s2))]
    matt1=[[0 for _ in range(len(s1))]for o in range(len(s2))]
    
    for i in range(1,len(s2)):
        for j in range(1,len(s1)):
            matt[i][j] = matt[i-1][j-1]+1
            if s2[i]!=s1[j]:
                matt1[i][j] = matt1[i-1][j-1]+1
            else:
                matt1[i][j]=matt1[i-1][j-1]
            while(matt1[i][j]>k):
                if (s1[1:][j-matt[i][j]]!=s2[1:][i-matt[i][j]]):
                    matt1[i][j]-=1
                matt[i][j]-=1
            maxim=max(maxim,matt[i][j])
    return maxim

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        first_multiple_input = input().rstrip().split()

        k = int(first_multiple_input[0])

        s1 = first_multiple_input[1]

        s2 = first_multiple_input[2]

        result = substringDiff(k, s1, s2)

        fptr.write(str(result) + '\n')

    fptr.close()
