#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'superReducedString' function below.
#
# The function is expected to return a STRING.
# The function accepts STRING s as parameter.
#

#if res is empty add the first char in s, then add the next one if its not rightmost element in res. For consecutive elements, we will just pop the prior element & continue the loop to next element, effectively removing all consecutive chars
def superReducedString(s):
    result = []
    for i in range(len(s)):
        if len(result)== 0 or result[-1]!= s[i]:
            result.append(s[i])
        else:
            result.pop()
    
    if len(result)==0:
        return "Empty String"
    else:
        return "".join(result)
            

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    s = input()

    result = superReducedString(s)

    fptr.write(result + '\n')

    fptr.close()