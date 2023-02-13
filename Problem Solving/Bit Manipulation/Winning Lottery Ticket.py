#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'winningLotteryTicket' function below.
#
# The function is expected to return a LONG_INTEGER.
# The function accepts STRING_ARRAY tickets as parameter.
#

def winningLotteryTicket(tickets):
    a='0123456789'
    t_count=[0]*1024
    for t in tickets:
        b=''
        for num in a:
            if num in t:
                b+='1'
            else:
                b+='0'
        b=int(b,2)
        t_count[b] +=1
    r=0
    for i1,t1 in enumerate(t_count[:1023]):
        if t1:
            for i2 in range(i1+1,1024):
                if (i1 | i2) == 1023:
                    r+=t1*t_count[i2]
    r+= (t_count[-1]*(t_count[-1]-1))//2
    return(r)
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    tickets = []

    for _ in range(n):
        tickets_item = input()
        tickets.append(tickets_item)

    result = winningLotteryTicket(tickets)

    fptr.write(str(result) + '\n')

    fptr.close()
