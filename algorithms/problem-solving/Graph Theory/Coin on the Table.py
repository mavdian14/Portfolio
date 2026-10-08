#!/bin/python3

import math
import os
import random
import re
import sys
sys.setrecursionlimit(10000)

#
# Complete the 'coinOnTheTable' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER m
#  2. INTEGER k
#  3. STRING_ARRAY board
#

def inBoard(i, j, board):
    return i >= 0 and i < len(board) and j >= 0 and j < len(board[i])

def DFS(i, j, costs, board, k, cost = 0, time = 0):
    if not inBoard(i, j, board) or cost >= costs[i][j]:
        return
    costs[i][j] = cost
    if board[i][j] == '*': 
        return
    if time == k :
        return
    DFS(i - 1, j, costs, board, k, cost if board[i][j] == 'U' else cost + 1, time + 1)
    DFS(i, j - 1, costs, board, k, cost if board[i][j] == 'L' else cost + 1, time + 1)
    DFS(i + 1, j, costs, board, k, cost if board[i][j] == 'D' else cost + 1, time + 1)
    DFS(i, j + 1, costs, board, k, cost if board[i][j] == 'R' else cost + 1, time + 1)
        
def coinOnTheTable(m, k, board, costs):
    DFS(0, 0, costs, board, k, 0, 0)
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == '*':
                minCost = costs[i][j]
                return -1 if minCost == math.inf else minCost

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    nmk = input().split()
    n = int(nmk[0])
    m = int(nmk[1])
    k = int(nmk[2])
    board = []
    costs = []
    for _ in range(n):
        board_item = input()
        board.append(board_item)
        costs.append([math.inf for ctr in range(len(board_item))])
    result = coinOnTheTable(m, k, board, costs)
    fptr.write(str(result) + '\n')
    fptr.close()
