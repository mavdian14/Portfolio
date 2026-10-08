#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'nimGame' function below.
#
# The function is expected to return a STRING.
# The function accepts INTEGER_ARRAY pile as parameter.
#

def nimGame(pile):
    res=0
    #if reduce(lambda x,y: x^y, pile) == 0 second will win. Reduce is used when you want to apply a function, in this case lambda, to an iterable, in this case pile, succesively in this case on each x,y (adjacent values). It will reduce the iterable to a single value by repeatedly applying x^y = a -> a ^ x_2 -> a_2 ^ y_2.
    for i in range(len(pile)):
        res ^= pile[i]
    
    if(res):
        return "First"
    else:
        return "Second"

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    g = int(input().strip())

    for g_itr in range(g):
        n = int(input().strip())

        pile = list(map(int, input().rstrip().split()))

        result = nimGame(pile)

        fptr.write(result + '\n')

    fptr.close()
