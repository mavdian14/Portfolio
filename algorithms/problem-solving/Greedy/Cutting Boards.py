#!/bin/python3

import math
import os
import random
import re
import sys

def boardCutting(cost_y, cost_x):
    cost_y.sort(reverse=True)
    cost_x.sort(reverse=True)
    y = 0
    x = 0
    cuts = 0
    
    while True:
        #Choose the largest costs first. If the costs are equal, it doesn't matter which one you do first. 
        if cost_y[y] > cost_x[x]:
            cuts += cost_y[y]*(x+1)
            y += 1
        else:
            cuts += cost_x[x]*(y+1)
            x += 1
            
        #Once one of the lists is depleated. Complete the remaining list and return the answer.  
        if x == len(cost_x):
            for i in range(len(cost_y)-y):
                cuts += cost_y[y+i]*(x+1)
            return cuts % (10**9 + 7)
        if y == len(cost_y):
            for i in range(len(cost_x)-x):
                cuts += cost_x[x+i]*(y+1)
            return cuts % (10**9 + 7)
        
            
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    q = int(input().strip())

    for q_itr in range(q):
        first_multiple_input = input().rstrip().split()

        m = int(first_multiple_input[0])

        n = int(first_multiple_input[1])

        cost_y = list(map(int, input().rstrip().split()))

        cost_x = list(map(int, input().rstrip().split()))

        result = boardCutting(cost_y, cost_x)

        fptr.write(str(result) + '\n')

    fptr.close()
