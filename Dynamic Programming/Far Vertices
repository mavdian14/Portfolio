#!/bin/python3

import math
import os
import random
import re
import sys

n, k = [int(a) for a in input().split(" ")]
count = 0

class Node(object):
    def __init__(self):
        self.neighbors = []
        self.marked = False

    def set_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def mark_dfs(self, depth, root = False):
        global count
        self.marked = True
        count += 1
        if depth == 0:
            children = len(self.neighbors) - 1
            if not root:
                return children
            return min(children, 1)
        num_children = 0
        for neighbor in self.neighbors:
            if not neighbor.marked:
                mc = neighbor.mark_dfs(depth-1)
                if root:
                    num_children = max(num_children,mc)
                else:
                    num_children += mc
        return num_children

nodes = []
for i in range(n):
    node = Node()
    nodes.append(node)

def unmark_all():
    for node in nodes:
        node.marked = False

for i in range(n - 1):
    u, v = [int(a) - 1 for a in input().split(" ")]
    nodes[u].set_neighbor(nodes[v])
    nodes[v].set_neighbor(nodes[u])
max_count = 0
for node in nodes:
    c = node.mark_dfs(k // 2, True)
    if k % 2 == 1:
        count += c
    if count > max_count:
        max_count = count
    unmark_all()
    count = 0  
print(n - max_count)
