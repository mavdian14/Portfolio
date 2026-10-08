#!/bin/python3

import math
import os
import random
import re
import sys
from collections import Counter
#
# Complete the 'gameOfThrones' function below.
#
# The function is expected to return a STRING.
# The function accepts STRING s as parameter.
#

def gameOfThrones(s):
    s = Counter(s)
    total = 0
    for key,value in s.items():
        #ideally for all characters, they appear an even amount of times except at most one character. If there is more than 1 character that appears an odd # of times, can't create a palindrome
        total += value%2
    
    if total > 1:
        return "NO"
    else:
        return "YES"

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    s = input()

    result = gameOfThrones(s)

    fptr.write(result + '\n')

    fptr.close()
