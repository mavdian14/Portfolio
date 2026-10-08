#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'twoPluses' function below.
#
# The function is expected to return an INTEGER.
# The function accepts STRING_ARRAY grid as parameter.
#

def twoPluses(grid):
    #create a border for the matrix
    temp = []
    temp.append(['O']*(m+2)) #first row
    for i in range(n):
        temp.append(['O'] + list(grid[i]) + ['O']) # grid rows
    temp.append(['O']*(m+2)) #last row 
    
    grid = temp
    
    answer = 0
    
    #iteratee for first plus
    for i in range(1,n+1):
        for j in range(1,m+1):
            #track the plus
            r = 0
            #check for good cell
            while grid[i+r][j] == "G" and grid[i-r][j] == "G" and grid[i][j+r] == "G" and grid[i][j-r] == "G":
                # to avoid overlap
                grid[i+r][j] = grid[i-r][j] = grid[i][j+r] = grid[i][j-r] = 'g'
                
                #iterate for 2nd plus
                for I in range(1,n+1):
                    for J in range(1,m+1):
                        #track the plus
                        R = 0
                        while grid[I+R][J] == "G" and grid[I-R][J] == "G" and grid[I][J+R] == "G" and grid[I][J-R] == "G":
                            answer = max(answer, (4*r + 1)*(4*R+1))
                            R+=1
                            
                r+=1
            #revert back all the occupied cells    
            r = 0
            while grid[i+r][j] == "g" and grid[i-r][j] == "g" and grid[i][j+r] == "g" and grid[i][j-r] == "g":
                grid[i+r][j] = grid[i-r][j] = grid[i][j+r] = grid[i][j-r] = 'G'
                r+=1
    return answer
                
            
                
                
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    m = int(first_multiple_input[1])

    grid = []

    for _ in range(n):
        grid_item = input()
        grid.append(grid_item)

    result = twoPluses(grid)

    fptr.write(str(result) + '\n')

    fptr.close()
