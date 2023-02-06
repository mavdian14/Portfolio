#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'appendAndDelete' function below.
#
# The function is expected to return a STRING.
# The function accepts following parameters:
#  1. STRING s
#  2. STRING t
#  3. INTEGER k
#

def appendAndDelete(s, t, k):
    count = 0
    #zip() is used to to create a tuple of the corresponding ith elemnts from 2 iterators i.e. ((s_1,t_1),...,(s_n),t_n))
    for i,j in zip(s,t):
        if i == j:
            count +=1
        else:
            break
    t_len = len(s) + len(t)
    
    #Case 1: t_len <= 2*count + k => YES
    #Case 2: perform exactly k operations - t_len%2 == k%2 => YES
    #Case 3: t_len < k
    
    #2*count signifies deleting and appending elements count times (i.e. the matching number of elements between t & s)
    if t_len <= 2*count + k and t_len%2 == k%2 or t_len<k:
        return "Yes"
    else:
        return "No"
            

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    s = input()

    t = input()

    k = int(input().strip())

    result = appendAndDelete(s, t, k)

    fptr.write(result + '\n')

    fptr.close()
