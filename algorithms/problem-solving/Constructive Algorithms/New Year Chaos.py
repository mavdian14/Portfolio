#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'minimumBribes' function below.
#
# The function accepts INTEGER_ARRAY q as parameter.
#

def minimumBribes(q):
    # Write your code here
    S = dict.fromkeys(q,0)
    curr_max = q[-1]
    count = 0
    for i in range(len(q)-1,-1,-1):
        if q[i]>curr_max:
            S[q[i]]= q[i]-i-1
            if S[q[i]]<=0:
                S[q[i]]=1
        else:
            curr_max=q[i]
            
        if S[q[i]]>2:
            print("Too chaotic")
            return
        
    print(sum(S.values()))
            

if __name__ == '__main__':
    t = int(input().strip())

    for t_itr in range(t):
        n = int(input().strip())

        q = list(map(int, input().rstrip().split()))

        minimumBribes(q)
