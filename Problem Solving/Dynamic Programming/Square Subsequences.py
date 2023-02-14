#!/bin/python3

import math
import os
import random
import re
import sys
from collections import Counter

def solveSub(s,size):
    s1 = s[:size]
    s1Len = len(s1)+1
    s2 = s[size:]
    s2Len = len(s2)+1
    sMatrix = [[0 for j in range(s2Len)] for i in range(s1Len)]
    for i in range(1,s1Len):
        for j in range(1,s2Len):
            if s1[i-1]==s2[j-1]:
                sMatrix[i][j]=sMatrix[i-1][j]+sMatrix[i][j-1]+1
            else:
                sMatrix[i][j]=sMatrix[i-1][j]+sMatrix[i][j-1]-sMatrix[i-1][j-1]
    return sMatrix[-1][-1]-sMatrix[-2][-1]

def squareSubsequences(s):
    count = sum(solveSub(s,i) for i in range(1,len(s)))
    return count%1000000007
    


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input())

    for t_itr in range(t):
        s = input()

        result = squareSubsequences(s)

        fptr.write(str(result) + '\n')

    fptr.close()
