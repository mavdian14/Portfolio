#!/bin/python3

import math
import os
import random
import re
import sys

from collections import Counter

n, m, root = map(int, input().split())
uniquenum = dict()
multipleset = dict()
adj = dict()
for _ in range(n - 1):
    n1, n2 = map(int, input().split())
    if n1 in adj:
        adj[n1].add(n2)
    else:
        adj[n1] = set([n2])
    if n2 in adj:
        adj[n2].add(n1)
    else:
        adj[n2] = set([n1])
colors = [int(input()) for _ in range(n)]
multiples = set(Counter(colors) - Counter(set(colors)))
colors.insert(0, 0)
totalcolors = len(set(colors[1:]))
stack = [root]
added = set([root])
visited = set()
while len(stack) > 0:
    node = stack[len(stack) - 1]
    if node not in visited:
        visited.add(node)
        for child in adj[node] - added:
            stack.append(child)
            added.add(child)
    else:
        if colors[node] in multiples:
            uniquenum[node] = 0
            multipleset[node] = set([colors[node]])
        else:
            uniquenum[node] = 1
            multipleset[node] = set()
        for child in adj[node] - added:
            uniquenum[node] += uniquenum[child]
            multipleset[node] |= multipleset[child]
        stack.pop()
        added.remove(node)   
for _ in range(m):
    node = int(input())
    print(uniquenum[node] + len(multipleset[node]))
