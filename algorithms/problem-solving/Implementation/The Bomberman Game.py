#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'bomberMan' function below.
#
# The function is expected to return a STRING_ARRAY.
# The function accepts following parameters:
#  1. INTEGER n
#  2. STRING_ARRAY grid
#

def bomberMan(n, grid):
    if n == 1:
        return grid
    
    #case: all cells filled with bomb (during even seconds)
    if n%2 == 0:
        return ['O'*c for i in range(r)]
    
    #case: alternate states
    n //=2 #to remove even states
    for q in range((n+1)%2+1):
        newgrid = [['O']*c for i in range(r)]
        
        #function for detonation
        def set(x,y):
            if 0<=x<r and 0<=y<c:
                newgrid[x][y] = '.'
        
        xi = [0,0,0,1,-1]
        yi = [0,-1,1,0,0]
        
        for x in range(r):
            for y in range(c):
                #check for bomb in adjacent cells
                if grid[x][y] == 'O':
                    #detonate the cell
                    for i,j in zip(xi,yi):
                        set(x+i,y+j)
                        
        grid = newgrid
        
    return ["".join(x) for x in grid]
        
        
    

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    r = int(first_multiple_input[0])

    c = int(first_multiple_input[1])

    n = int(first_multiple_input[2])

    grid = []

    for _ in range(r):
        grid_item = input()
        grid.append(grid_item)

    result = bomberMan(n, grid)

    fptr.write('\n'.join(result))
    fptr.write('\n')

    fptr.close()
