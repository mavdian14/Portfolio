#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'cipher' function below.
#
# The function is expected to return a STRING.
# The function accepts following parameters:
#  1. INTEGER k
#  2. STRING s
#

def cipher(k, s):
    orig=""
    number_of_ones=0
    for i,b in enumerate(s[:len(s)-k+1]):
        if i>=k:
            if orig[i-k]=="1":
                number_of_ones-=1
        
        if (b=="1" and number_of_ones%2==0) or (b=="0" and number_of_ones%2==1):
            orig+="1"
            number_of_ones+=1
        else:
            orig+="0"
    
    return orig

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    k = int(first_multiple_input[1])

    s = input()

    result = cipher(k, s)

    fptr.write(result + '\n')

    fptr.close()
