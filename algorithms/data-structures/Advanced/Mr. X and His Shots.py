#!/bin/python3

import math
import os
import random
import re
import sys
import bisect
from bisect import bisect_left, bisect_right, insort
#
# Complete the 'solve' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. 2D_INTEGER_ARRAY shots
#  2. 2D_INTEGER_ARRAY players
#

def solve(shots, players):
    slower, shigher = [], []
    for s in shots:
        #insort inserts an element into an already sorted list
        insort(slower, s[0])
        insort(shigher,s[1])
    result = 0
    for p in players:
        #bisect_left returns the left most place in a sorted list to insert the given element; right-most place for bisect_right
        start=min(bisect_left(slower,p[0]),bisect_left(shigher,p[0]))
        end=max(bisect_right(shigher,p[1]),bisect_right(slower,p[1]))
        result += end-start
    return result

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    m = int(first_multiple_input[1])

    shots = []

    for _ in range(n):
        shots.append(list(map(int, input().rstrip().split())))

    players = []

    for _ in range(m):
        players.append(list(map(int, input().rstrip().split())))

    result = solve(shots, players)

    fptr.write(str(result) + '\n')

    fptr.close()
