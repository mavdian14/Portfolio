#!/bin/python3

import math
import os
import random
import re
import sys
from collections import Counter
#
# Complete the 'isValid' function below.
#
# The function is expected to return a STRING.
# The function accepts STRING s as parameter.
#

def isValid(s):
    cnt = Counter(s)
    
    #case 1: same frequency each char, .values() returns the values of the dictionary as a list
    if len(set(cnt.values())) ==1:
        return "YES"
    
    #case 2: more than 2 unique freq
    elif len(set(cnt.values())) > 2:
        return "NO"
    
    #case 3: 2 unique frequencies
    else:
        for key in cnt:
            cnt[key] -=1
            temp = list(cnt.values())
            #remove zeroes
            try:
                temp.remove(0)
            except:
                pass
            if len(set(temp)) == 1:
                return "YES"
            else:
                cnt[key] += 1
        return "NO"

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    s = input()

    result = isValid(s)

    fptr.write(result + '\n')

    fptr.close()
