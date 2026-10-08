#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'permutationGame' function below.
#
# The function is expected to return a STRING.
# The function accepts INTEGER_ARRAY arr as parameter.
#

def permutationGame(arr):
    isIncreasing = lambda arr: all([arr[i] < arr[i + 1] for i in range(len(arr) - 1)])
    
    memo = {}
 
    def findWinner(arr):
        key = tuple(arr)
        if key in memo: return memo[key]
        
    # If arr is ascending, then this player wins (base case)
        if isIncreasing(arr): 
            memo[key] = True; return True
    
    # Calculate next turns: If next player has any available winning moves, this player lost
        for idx in range(len(arr)):
            if findWinner(arr[:idx] + arr[idx + 1:]): memo[key] = False; return False 
            
    # Otherwise, this player wins because next player has no winning moves available
        memo[key] = True; return True 
   
    return 'Bob' if findWinner(arr) else 'Alice'

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        arr_count = int(input().strip())

        arr = list(map(int, input().rstrip().split()))

        result = permutationGame(arr)

        fptr.write(result + '\n')

    fptr.close()
