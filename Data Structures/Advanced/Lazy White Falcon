#!/bin/python3

import math
import os
import random
import re
import sys

from collections import defaultdict, deque
import sys

def read():
    return (int(s) for s in sys.stdin.readline().split())

N, Q = read()
adj_matrix = defaultdict(list)
for _ in range(N - 1):
    x, y = read()
    adj_matrix[x].append(y)
    adj_matrix[y].append(x)
segment_size = 120
parents = [None] * N
s_parent = [None] * N
s_weight = [0] * N
levels = [0] * N
update = [-1] * N
refresh = [-1] * N
weight = [0] * N
def refresh_segment(node, sp, tick):
    if node == sp or refresh[node] >= update[sp]:
        return
    parent = parents[node]
    if parent == sp:
        s_weight[node] = weight[parent]
    else:
        refresh_segment(parent, sp, tick)
        s_weight[node] = s_weight[parent] + weight[parent]
    refresh[node] = tick

# Initialize above with BFS, que is (segment parent, parent, node, level)
que = deque([(0, 0, 0, 0)])
while que:
    segment, parent, node, level = que.popleft()
    s_parent[node] = segment
    parents[node] = parent
    levels[node] = level
    child_segment = segment if level % segment_size else node
    for n in adj_matrix[node]:
        if n != parent:
            que.append((child_segment, node, n, level + 1))
results = []
for i in range(Q):
    op, u, x = read()
    if op == 1:
        weight[u] = x
        if levels[u] % segment_size:
            update[s_parent[u]] = i
        else:
            update[u] = i
    else:
        if levels[u] > levels[x]:
            u, x = x, u
        result = weight[x] + weight[u]
        # Traverse x upwards segment by segment until
        # levels[segments[x]] == levels[segments[u]]
        u_s = s_parent[u]
        while levels[s_parent[x]] > levels[u_s]:
            refresh_segment(x, s_parent[x], i)
            result += s_weight[x]
            x = s_parent[x]
        while s_parent[x] != s_parent[u]:
            refresh_segment(x, s_parent[x], i)
            refresh_segment(u, s_parent[u], i)
            result += s_weight[x]
            result += s_weight[u]
            x = s_parent[x]
            u = s_parent[u]
        for _ in range(levels[x] - levels[u]):
            x = parents[x]
            result += weight[x]
        while u != x:
            x = parents[x]
            u = parents[u]
            result += weight[x]
            result += weight[u]
        result -= weight[x]
        results.append(result)
print('\n'.join(str(x) for x in results))
