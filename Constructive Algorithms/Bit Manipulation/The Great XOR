#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'theGreatXor' function below.
#
# The function is expected to return a LONG_INTEGER.
# The function accepts LONG_INTEGER x as parameter.
#

def theGreatXor(x):
    binary=""
    for bit in bin(x)[2:]:
        binary+='0' if bit=='1' else '1'
    return(int(binary,2))

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    q = int(input().strip())

    for q_itr in range(q):
        x = int(input().strip())

        result = theGreatXor(x)

        fptr.write(str(result) + '\n')

    fptr.close()
