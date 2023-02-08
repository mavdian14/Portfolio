#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'beautifulPath' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. 2D_INTEGER_ARRAY edges
#  2. INTEGER A
#  3. INTEGER B
#

n, e = map(int, input().split())
graph = dict((i, set()) for i in range(1, n+1))
costs = [[2000]*(n+1) for i in range(0, n+1)]
for _ in range(e):
    a, b, w = map(int, input().split())
    if w < costs[a][b]:
        costs[a][b] = w
        costs[b][a] = w
        graph[a].add(b)
        graph[b].add(a)
start, end = map(int, input().split())
cost_log = [set() for j in range(n+1)]
queue = {(start, 0)}
while queue:
    (no, cost) = queue.pop()
    for ne in graph[no]:
        new_cost = costs[no][ne] | cost
        if new_cost not in cost_log[ne] and new_cost <= 1024:
            cost_log[ne].add(new_cost)
            queue.add((ne, new_cost))
print(sorted(cost_log[end])[0] if cost_log[end] else '-1')
