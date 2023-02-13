#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'pickingNumbers' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER_ARRAY a as parameter.
#

def pickingNumbers(a):
    result=0
    #create a set of the checked starting index we use to find the largest subsequences
    checked=set()
    for i in range(len(a)):
        if i not in checked:
            #.count() methods returns the number of elements in a with value a[i] in this case
            maxCount = max(a.count(a[i])+a.count(a[i]+1),a.count(a[i])+a.count(a[i]-1))
            if maxCount > result:
                result=maxCount
            checked.add(i)
    return result
    

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    a = list(map(int, input().rstrip().split()))

    result = pickingNumbers(a)

    fptr.write(str(result) + '\n')

    fptr.close()
