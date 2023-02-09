#!/bin/python3

import math
import os
import random
import re
import sys
from heapq import heapify, heappush, heappop

def minimumAverage(customers):
    heapify(customers)

    t = 0
    effy = []
    res = []
    while customers or effy:
        while not effy or (customers and customers[0][0] <= t):
            temp = heappop(customers)
            heappush(effy, (temp[1], temp[0]))

        c = heappop(effy)
        extra = (t - c[1]) * (t - c[1] > 0)
        res.append(c[0] +  extra)
        t = sum(c) + extra
            
    return int(sum(res) / len(res))

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    customers = []

    for _ in range(n):
        customers.append(list(map(int, input().rstrip().split())))

    result = minimumAverage(customers)

    fptr.write(str(result) + '\n')

    fptr.close()
