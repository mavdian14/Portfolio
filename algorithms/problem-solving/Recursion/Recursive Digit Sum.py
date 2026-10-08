#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'superDigit' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. STRING n
#  2. INTEGER k
#

def super_digit(digit):
    if digit<10:
        return digit
    
    sum_digits=0
    while digit:
        sum_digits+= digit%10
        digit = digit//10
    return super_digit(sum_digits)
    
def superDigit(n, k):
    digit = sum(int(num) for num in n)
    result=super_digit(digit*k)
    return result

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = first_multiple_input[0]

    k = int(first_multiple_input[1])

    result = superDigit(n, k)

    fptr.write(str(result) + '\n')

    fptr.close()
