#!/bin/python3

import math
import os
import random
import re
import sys

from collections import deque

def tuplify(x):
    return tuple(tuple(i) for i in x)
    
def moves(rods):
    #num of rods
    for x in range(4):
        #if rods[x] not empty
        if rods[x]:
            for y in range(4):
                if not rods[y] or rods[y][-1] > rods[x][-1]:
                    #yield in this case returns (x,y)
                    yield(x,y)

def do_move(rods,x,y):
    rods = [list(r) for r in rods]
    rods[y].append(rods[x].pop())
    rods[1:4] = sorted(rods[1:4], key = lambda t: t[-1] if t else 0)
    return tuplify(rods)
 
#bfs, breadth-first-search is an algo used for tree traversal on graphs/tree data structures. Steps: 1. pick any node, visit the adjacent unvisited vertex, mark it visited, display it & insert it into a queue. 2. if there are no more adjacent vertices left, remove the 1st vertex from the queue. 3. Repeat steps 1 & 2 until the queue is empty or desired node is found
def bfs(rods,n):
    start = (tuplify(rods),0)
    visited = set()
    visited.add(start)
    q=deque([start])
    while q:
        cur,depth = q.popleft()
        if all(len(r) == 0 for r in cur[1:]):
            return depth
        for x,y in moves(cur):
            child = do_move(cur,x,y)
            if child not in visited:
                visited.add(child)
                q.append((child,depth + 1))
    return -1
    
n = int(input())
rods = [[] for _ in range(4)]
for i, disk in enumerate(map(int,input().split())):
    rods[disk-1] = [i] + rods[disk-1]
print(bfs(rods,n))
