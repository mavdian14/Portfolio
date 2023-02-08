#!/bin/python3

import os
import sys

#
# Complete the solve function below.
#
def solve(t):
    ranges, n = [], len(t)
    for i,e in enumerate(t):
        if e >= n or e == 0:
            #skip those that need to much time & those who are already finished
            continue
        #add range from start (2nd value is 0) to end (is 1)
        ranges.extend([((i-n+1+n)%n+1, 0), ((i-e+n)%n+1,1)])
    ranges.sort(key=lambda e: (e[0], e[1]))
    #max opened ranges, currently opened ranges &   first index of max opened range
    max_, current, first_index = 0,0,1
    for _ in range(2): # walk twice around a table
            for i,v in ranges:
                if max_ == current:
                    first_index = min(i,first_index) # get lowest index for all maxes
                if v == 0: #beginning of range
                    current +=1
                    if max_ < current:
                        max_ = current
                        first_index = i #set new first index
                else:
                    current -= 1
    return first_index
                        
    

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t_count = int(input())

    t = list(map(int, input().rstrip().split()))

    id = solve(t)

    fptr.write(str(id) + '\n')

    fptr.close()
