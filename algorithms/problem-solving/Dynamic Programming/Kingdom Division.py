#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'kingdomDivision' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER n
#  2. 2D_INTEGER_ARRAY roads
#

def kingdomDivision(n, roads):
    mod = 1000000007
    adj = {}

    for item in roads:
        parent = item[0]
        child = item[1]

        if parent not in adj.keys():
            adj[parent] = []

        if child not in adj.keys():
            adj[child] = []

        adj[parent].append(child)
        adj[child].append(parent)

    
    
    iter_list = {}

    for key in adj.keys():
        iter_list[key] = iter(adj[key])

    # dfs begins using stack
    stack = [1]

    good_conf = {}
    bad_conf = {}
    visited = set()
    visited.add(1)
    children = {}

    while stack:
        source = stack[-1]
             
        iterator = iter_list[source]  # get the item at the peek
    
        try:
            to = next(iterator)
            if to not in visited:
                stack.append(to)
                visited.add(to)
                
                if source not in children.keys():
                    children[source] = []
                    
                children[source].append(to)

        except StopIteration: 
                
                key = stack.pop()

                good_conf[key] = 1
                bad_conf[key] = 1
                
                if key not in children.keys():
                    good_conf[key] = 0
                    bad_conf[key] = 1
                    continue
            
                
                for child in children[key]:
                    
                    good_conf[key] = (good_conf[key] * (2 * good_conf[child] + bad_conf[child])) % mod
                    bad_conf[key] = (bad_conf[key] * good_conf[child]) % mod

                good_conf[key] = good_conf[key] - bad_conf[key]
                
                
                while good_conf[key] < 0: 

                    good_conf[key] += mod

    return (good_conf[1] * 2) % mod
                

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    roads = []

    for _ in range(n - 1):
        roads.append(list(map(int, input().rstrip().split())))

    result = kingdomDivision(n, roads)

    fptr.write(str(result) + '\n')

    fptr.close()
