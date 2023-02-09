#!/bin/python3

import math
import os
import random
import re
import sys
from collections import defaultdict

def recursive_solve(node, path_dict, res_dict):
    if node in res_dict:
        return res_dict[node]
    if node not in path_dict:
        res_dict[node] = 0
        return 0
    child_list = path_dict[node]
    mex_set = set()
    for c in child_list:
        grundy_c = recursive_solve(c, path_dict, res_dict)
        mex_set.add(grundy_c)
        
    grundy = 0
    while grundy in mex_set:
        grundy += 1
    
    res_dict[node] = grundy
    return grundy

def bendersPlay(n, paths, query):
    k = len(query)
    soldier_dict = defaultdict(int)
    for i in range(k):
        b_i = query[i]
        soldier_dict[b_i] += 1
    
    res = 0
    for b_i, num in soldier_dict.items():
        if num % 2 == 0:
            continue
        new = recursive_solve(b_i, path_dict, res_dict)
        res ^= new
    winner = "Iroh" if res == 0 else "Bumi"
    return winner

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    m = int(first_multiple_input[1])

    paths = []

    for _ in range(m):
        paths.append(list(map(int, input().rstrip().split())))
    
    path_dict = defaultdict(list)
    for i in range(m):
        u, v = paths[i]
        path_dict[u].append(v)
    
    res_dict = dict()    

    q = int(input().strip())

    for q_itr in range(q):
        query_count = int(input().strip())

        query = list(map(int, input().rstrip().split()))

        result = bendersPlay(n, paths, query)

        fptr.write(result + '\n')

    fptr.close()
