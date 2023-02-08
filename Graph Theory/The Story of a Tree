#!/bin/python3

import math
import os
import random
import re
import sys
import fractions
from fractions import Fraction
#
# Complete the 'storyOfATree' function below.
#
# The function is expected to return a STRING.
# The function accepts following parameters:
#  1. INTEGER n
#  2. 2D_INTEGER_ARRAY edges
#  3. INTEGER k
#  4. 2D_INTEGER_ARRAY guesses
#
def dfs(v, adj_list, parent):
    for u in adj_list[v]:
        if u != parent[v]:
            parent[u] = v
            dfs(u, adj_list, parent)

            
def sum_dfs(v, p, adj_list, count, k):
    count[v] += int(p != -1) * count[p]
    out = count[v] >= k
    for u in adj_list[v]:
        if u != p:
            out += sum_dfs(u, v, adj_list, count, k)
    return out

def storyOfATree(n, edges, k, guesses):
    adj_list = {i:set() for i in range(n)}
    for u, v in edges:
        adj_list[u-1].add(v-1)
        adj_list[v-1].add(u-1)  
    parent, count = [0]*n, [0]*n
    dfs(0, adj_list, parent)
    for u, v in guesses:
        if parent[v-1] == u-1:
            count[0] += 1
            count[v-1] -= 1
        else:
            count[u-1] += 1
    n_correct = sum_dfs(0, -1, adj_list, count, k)
    out = Fraction(n_correct, n)
    return f"{out.numerator}/{out.denominator}"

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    q = int(input().strip())

    for q_itr in range(q):
        n = int(input().strip())

        edges = []

        for _ in range(n - 1):
            edges.append(list(map(int, input().rstrip().split())))

        first_multiple_input = input().rstrip().split()

        g = int(first_multiple_input[0])

        k = int(first_multiple_input[1])

        guesses = []

        for _ in range(g):
            guesses.append(list(map(int, input().rstrip().split())))

        result = storyOfATree(n, edges, k, guesses)

        fptr.write(result + '\n')

    fptr.close()
