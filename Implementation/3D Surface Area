#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'surfaceArea' function below.
#
# The function is expected to return an INTEGER.
# The function accepts 2D_INTEGER_ARRAY A as parameter.
#

def surfaceArea(A):
    #calculate area of top and bottom
    area = 2 * H * W
    
    #checks the limit
    def check(i,j):
        return A[x+i][y+j] if 0<=x+i<H and 0<=y+j<W else 0
    
    #remaining surfaces
    xi = [0,0,1,-1]
    yi = [1,-1,0,0]
    
    for x in range(H):
        for y in range(W):
            for i,j in zip(xi,yi):
                area += max(0,A[x][y] - check(i,j))
    
    return area
                
    

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    H = int(first_multiple_input[0])

    W = int(first_multiple_input[1])

    A = []

    for _ in range(H):
        A.append(list(map(int, input().rstrip().split())))

    result = surfaceArea(A)

    fptr.write(str(result) + '\n')

    fptr.close()
