#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'countLuck' function below.
#
# The function is expected to return a STRING.
# The function accepts following parameters:
#  1. STRING_ARRAY matrix
#  2. INTEGER k
#

def countLuck(matrix, k):
    for i in range(n):
        for j in range(m):
            if matrix[i][j]=='M':
                start=(i,j)
            if matrix[i][j]=='*':
                end=(i,j)
    visit={}
    cur=[(start,0)] #record every step
    while cur:
        nex=[]
        for (p,q),turn in cur:
            if (p,q)==end:
                return 'Impressed' if turn==k else 'Oops!'
            if (p,q) not in visit:
                visit[(p,q)]=turn
                nexpoint=[]
                for (i,j) in [(0,1),(0,-1),(-1,0),(1,0)]:
                    if 0<=p+i<n and 0<=q+j<m and matrix[p+i][q+j]!='X' and (p+i,j+q) not in visit:
                        nexpoint.append((p+i,q+j))
                #if expansion steps >=2 then turning point+1
                count=1 if len(nexpoint)>=2 else 0
                #push new step into next step
                for (i,j) in nexpoint:
                    nex.append(((i,j),turn+count))
        cur=nex #next becomes current step
            

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        first_multiple_input = input().rstrip().split()

        n = int(first_multiple_input[0])

        m = int(first_multiple_input[1])

        matrix = []

        for _ in range(n):
            matrix_item = input()
            matrix.append(matrix_item)

        k = int(input().strip())

        result = countLuck(matrix, k)

        fptr.write(result + '\n')

    fptr.close()
