#!/bin/python3

import math
import os
import random
import re
import sys

def stoneDivision(n, s):
    if len([q for q in s if n%q==0 and q%2==0])>0:
        return "First"
    fulldata = {}
    queue=[n]
    start=0
    while start<len(queue):
        if queue[start] not in fulldata:
            fulldata[queue[start]]=[queue[start]//q for q in s if queue[start]%q==0 and q>1]
            queue=queue+fulldata[queue[start]]
        start+=1
    funct={}
    for gg in sorted(fulldata.keys()):
        funct[gg]=1-min(map(lambda g:funct[g],fulldata[gg]),default=1)
    return "First" if funct[n]%2 else "Second"

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    m = int(first_multiple_input[1])

    s = list(map(int, input().rstrip().split()))

    result = stoneDivision(n, s)

    fptr.write(result + '\n')

    fptr.close()
