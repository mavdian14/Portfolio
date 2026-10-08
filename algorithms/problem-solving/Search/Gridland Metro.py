#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'gridlandMetro' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER n
#  2. INTEGER m
#  3. INTEGER k
#  4. 2D_INTEGER_ARRAY track

#non-overlapping example
# 1 1 2
# 1 3 4
# 3 > 2

#overlapping example
#1 1 3
#1 2 4
#4 > 3

#n=rows,m=columns,k=# of tracks to be mapped
def gridlandMetro(n, m, k, track):
    d = {}
    total = n*m
    for i in range(k):
        r = track[i][0]
        c1 = track[i][1]
        c2 = track[i][2]
        
        #case 1: if train track not in d
        if r not in d:
            d[r] = [c1,c2]
        # track not overlapping, then update total
        elif c1 > d[r][1]:
            total -= c2-c1+1
        # track is overlapping, then update it
        elif c2 > d[r][1]:
            d[r][1] = c2
        
    #main logic
    tracks = 0
    for r in d:
        tracks += d[r][1] - d[r][0] + 1
    
    lamps = total - tracks
    return lamps
        
            
        
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    m = int(first_multiple_input[1])

    k = int(first_multiple_input[2])

    track = []

    for _ in range(k):
        track.append(list(map(int, input().rstrip().split())))

    result = gridlandMetro(n, m, k, track)

    fptr.write(str(result) + '\n')

    fptr.close()
