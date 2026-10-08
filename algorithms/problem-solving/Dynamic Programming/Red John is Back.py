#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'redJohn' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER n as parameter.
#
def is_prime(n):
    if n%2==0 and n>2:
        return False
    for i in range(3,int(math.sqrt(n))+1,2):
        if n%i==0:
            return False
    return True
    
def redJohn(n):
    maxHorizontals=n//4
    M=0
    for i in range(maxHorizontals+1):
        simplifiedN = n-(i*3)
        M += int(math.factorial(simplifiedN) / (math.factorial(i) * math.factorial(simplifiedN - i)))
    
    ans=0
    for i in range(M+1):
        if i > 1 and is_prime(i):
            ans+=1
    return ans
    
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        n = int(input().strip())

        result = redJohn(n)

        fptr.write(str(result) + '\n')

    fptr.close()
