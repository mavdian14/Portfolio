#!/bin/python3

import math
import os
import random
import re
import sys
from collections import deque

#
# Complete the 'printShortestPath' function below.
#
# The function accepts following parameters:
#  1. INTEGER n
#  2. INTEGER i_start
#  3. INTEGER j_start
#  4. INTEGER i_end
#  5. INTEGER j_end
#

def printShortestPath(n, i_start, j_start, i_end, j_end):
    # Print the distance along with the sequence of moves.
    def check_pairs(i,j,n):
        possible_pairs = [(i-2,j-1, 'UL'), (i-2,j+1, 'UR'), (i,j+2,'R'), (i+2,j+1, 'LR'), (i+2,j-1,'LL'), (i,j-2,'L')]
        
        moves = {}
        for x in possible_pairs:
            if 0 <= x[0] < n and 0 <= x[1] < n:
                moves[x] = 1
        
        return moves
    
    def bfs(a,b,x,y,n):
        q = deque([(a,b, 0, [])])
        visited = {(a,b): 1}
        while q:
            i,j,count,path = q.popleft()
            pos_pairs = check_pairs(i,j,n)
            for pair in pos_pairs:
                coord = (pair[0],pair[1])
                new_path = path + [pair[2]]
                if coord == (x,y):
                    print(count+1)
                    print(*new_path)
                    return
                if coord not in visited:
                    visited[coord] = 1
                    q.append((coord[0],coord[1], count+1, new_path))
                    
        print("Impossible")
            
        

    bfs(i_start, j_start, i_end, j_end,n)
    

if __name__ == '__main__':
    n = int(input().strip())

    first_multiple_input = input().rstrip().split()

    i_start = int(first_multiple_input[0])

    j_start = int(first_multiple_input[1])

    i_end = int(first_multiple_input[2])

    j_end = int(first_multiple_input[3])

    printShortestPath(n, i_start, j_start, i_end, j_end)
