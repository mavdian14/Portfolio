#!/bin/python3

import math
import os
import random
import re
import sys
from collections import Counter
#
# Complete the 'happyLadybugs' function below.
#
# The function is expected to return a STRING.
# The function accepts STRING b as parameter.
#

def happyLadybugs(b):
    bugs = Counter(b)
    for i,j in bugs.items():
        #case where # of ladybugs is 1
        if i != "_" and j == 1:
            return "NO"
    
    #check if 1 empty cell is present        
    if bugs["_"] > 0:
        return "YES"
    else:
        #check the lady bugs are happy initially
        pair = 0
        for i in range(len(b)-1):
            if b[i] == b[i+1]:
                pair += 1
            elif pair > 0:
                pair = 0
            else:
                return "NO"
            
    return "YES"

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    g = int(input().strip())

    for g_itr in range(g):
        n = int(input().strip())

        b = input()

        result = happyLadybugs(b)

        fptr.write(result + '\n')

    fptr.close()
 
