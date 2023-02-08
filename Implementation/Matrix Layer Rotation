#!/bin/python3

import math
import os
import random
import re
import sys

def matrixRotation(matrix, r):
    n, m = len(matrix), len(matrix[0])
    def to_depth_pos(i, j):
        depth = min(i, j, n-i-1, m-j-1)
        if j == depth:
            pos = i - depth
        elif i == n-1-depth:
            pos = n - 1 + j - 3*depth
        elif j == m-1-depth:
            pos = 2*n + m - 3 - i - 5*depth
        else:
            pos = 2*n + 2*m - 4 - j - 7*depth
        return depth, pos

    def from_depth_pos(depth, pos):
        pos = pos % (2*(n + m - 2 - 4*depth))
        if pos < n-1-2*depth:
            j, i = depth, pos+depth
        elif pos < n + m - 2 - 4*depth:
            i, j = n-1-depth, pos - (n - 1 - 3*depth)
        elif pos < 2*n + m - 3 - 6*depth:
            j, i = m-1-depth, 2*n + m - 3 - 5*depth - pos
        else:
            i, j = depth,     2*n + 2*m - 4 - 7*depth - pos
        return i, j
    
    for i in range(n):
        for j in range(m):
            depth, pos = to_depth_pos(i, j)
            new_i, new_j = from_depth_pos(depth, pos-r)
            print(matrix[new_i][new_j], end=' ')
        print()

if __name__ == '__main__':
    first_multiple_input = input().rstrip().split()

    m = int(first_multiple_input[0])

    n = int(first_multiple_input[1])

    r = int(first_multiple_input[2])

    matrix = []

    for _ in range(m):
        matrix.append(list(map(int, input().rstrip().split())))

    matrixRotation(matrix, r)
