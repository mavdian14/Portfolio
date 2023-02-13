#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'knightlOnAChessboard' function below.
#
# The function is expected to return a 2D_INTEGER_ARRAY.
# The function accepts INTEGER n as parameter.
#

def knightlOnAChessboard(n):
    from collections import deque
    
    def get_min_moves(a: int, b: int) -> int:
        q = deque([((0, 0), 0)])
        visited = {(0, 0)}
        
        while q:
            coord, dist = q.popleft()
            i, j = coord
            next_coords = [
                (i + a, j + b), (i + b, j + a),
                (i + a, j - b), (i + b, j - a),
                (i - a, j + b), (i - b, j + a),
                (i - a, j - b), (i - b, j - a),
            ]
            for ni, nj in next_coords:
                if 0 <= ni < n and 0 <= nj < n:
                    if (ni, nj) in visited:
                        continue
                    if ni == nj == n - 1:
                        return dist + 1
                    q.append(((ni, nj), dist + 1))
                    visited.add((ni, nj))
        return -1        

    res = [[None] * (n - 1) for _ in range(n - 1)]
    for i in range(n - 1):
        for j in range(i + 1):
            res[i][j] = res[j][i] = get_min_moves(i + 1, j + 1)
    return res

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    result = knightlOnAChessboard(n)

    fptr.write('\n'.join([' '.join(map(str, x)) for x in result]))
    fptr.write('\n')

    fptr.close()
