#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'deforestation' function below.
#
# The function is expected to return a STRING.
# The function accepts following parameters:
#  1. INTEGER n
#  2. 2D_INTEGER_ARRAY tree
#
from functools import reduce
from operator import xor

def deforestation(n, tree):
    root = build_tree(n,tree)
    return 'Alice' if grundy(root) else 'Bob'

def build_tree(n,edges):
    neighbours = [set() for _ in range(n+1)]
    for u,v in edges:
        neighbours[u].add(v)
        neighbours[v].add(u)
    def get_branch(parent,me):
        return [get_branch(me,c) for c in neighbours[me] if c !=parent]
    return [get_branch(1,c) for c in neighbours[1]]
    
def grundy(family):
    return reduce(xor, (1+grundy(branch) for branch in family),0) 

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        n = int(input().strip())

        tree = []

        for _ in range(n - 1):
            tree.append(list(map(int, input().rstrip().split())))

        result = deforestation(n, tree)

        fptr.write(result + '\n')

    fptr.close()
