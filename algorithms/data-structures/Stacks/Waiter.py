#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'waiter' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts following parameters:
#  1. INTEGER_ARRAY number
#  2. INTEGER q
#

def waiter(number, q):
    lower = 2
    upper = 10000
    p = [i for i in range(lower, upper + 1) if all(i % j != 0 for j in range(2, i))]
    
    ans = []
    stackA = []
    stackB = []

    for i in range(q):
        if i == 0:
            s = number
        else:
            s = stackA
            stackA = []
                        
        for j in range(len(s)):  
            x = s.pop()
            if x % p[i] == 0:
                stackB.append(x)
            else:
                stackA.append(x)
        while stackB:
            ans.append(stackB.pop())
    
    while stackA:
        ans.append(stackA.pop())
    return ans
            
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    q = int(first_multiple_input[1])

    number = list(map(int, input().rstrip().split()))

    result = waiter(number, q)

    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
