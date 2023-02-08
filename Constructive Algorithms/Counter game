#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'counterGame' function below.
#
# The function is expected to return a STRING.
# The function accepts LONG_INTEGER n as parameter.
#
def count_one(s):
    count=0
    for i in s:
        if i =='1':
            count+=1
    return count

def count_zero_from_end(s):
    count=0
    s=list(s)
    end_digit=s.pop()
    if end_digit=="1":
        return 0
    else:
        count+=1
    while(s.pop() != '1'):
        count+=1
    return count

def counterGame(n):
    # Write your code here
    binary = format(n, "b")
    ones = count_one(binary)
    zeros_from_end = count_zero_from_end(binary)
    return "Louise" if (ones + zeros_from_end) % 2 == 0 else "Richard"

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        n = int(input().strip())

        result = counterGame(n)

        fptr.write(result + '\n')

    fptr.close()
