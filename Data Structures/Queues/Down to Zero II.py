#!/bin/python3

import math
import os
import random
import re
import sys
from math import sqrt
from collections import deque
#
# Complete the 'downToZero' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER n as parameter.
#

def downToZero(n):
    # will number with # of moves to get to that number
    memo = set()
    count = 0
    q = deque([[n,count]])
    while q:
        n,count = q.popleft()
        #base case
        if n <= 1:
            if n == 1:
                count+=1
            break
        #general cases:
        #2nd operation
        if n-1 not in memo:
            memo.add(n-1)
            q.append([n-1,count+1])
        
        #range() here has start_val=sqrt(n),stop_val=1,step_val=-1
        for i in range(int(sqrt(n)),1,-1):
            if n%i == 0:
                factor = max(n//i,i)
                if factor not in memo:
                    memo.add(factor)
                    q.append([factor,count+1])
    
    return count
            

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    q = int(input().strip())

    for q_itr in range(q):
        n = int(input().strip())

        result = downToZero(n)

        fptr.write(str(result) + '\n')

    fptr.close()
