#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'gridChallenge' function below.
#
# The function is expected to return a STRING.
# The function accepts STRING_ARRAY grid as parameter.
#

def gridChallenge(grid):
    #convert this string into individual characters & store them in a list
    grid = [list(row) for row in grid]
    #r = len(row), c=len(col)
    r=len(grid)
    c=len(grid[0])
    #sorts the elements in each row
    for i in range(r):
        grid[i].sort()
        
    #verifying the elements by column are sort alphabetically    
    for j in range(c):
        for i in range(1,r):
            if not grid[i-1][j] <= grid[i][j]:
                return "NO"
    return "YES"
    
            

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        n = int(input().strip())

        grid = []

        for _ in range(n):
            grid_item = input()
            grid.append(grid_item)

        result = gridChallenge(grid)

        fptr.write(result + '\n')

    fptr.close()
