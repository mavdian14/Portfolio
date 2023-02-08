#!/bin/python3

import math
import os
import random
import re
import sys
from operator import itemgetter
from itertools import groupby
from bisect import bisect

class Node:
    """Represents an element of a set."""
    def __init__(self, id):
        self.id = id
        self.parent = self
        self.rank = 0
        self.size = 1
        self.paths = 0

    def __repr__(self):
        #!r converts the object, here self.id into a representation using str.format()
        return 'Node({!r})'.format(self.id)


def Find(x):
    """Returns the representative object of the set containing x."""
    if x.parent is not x:
        x.parent = Find(x.parent)
    return x.parent


def Union(x, y):
    xroot = Find(x)
    yroot = Find(y)

    # x and y are already in the same set
    if xroot is yroot:
        return 0

    # x and y are not in same set, so we merge them
    if xroot.rank < yroot.rank:
        xroot, yroot = yroot, xroot  # swap xroot and yroot

    new_paths = xroot.size * yroot.size
    xroot.paths += yroot.paths + new_paths
    
    # merge yroot into xroot
    yroot.parent = xroot
    xroot.size += yroot.size
    
    if xroot.rank == yroot.rank:
        xroot.rank = xroot.rank + 1
    
    return new_paths

# Complete the solve function below.
def solve(tree, queries):
    tree.sort(key=itemgetter(2))
    
    weights, path_count = [0], [0]
    nodes = {}
    #itemgetter(n) constructs a callable that assumes an iterable object i.e. list,tuple,set & fetches the nth element from it
    for k, g in groupby(tree, key=itemgetter(2)):
        total = path_count[-1]
        #.setdefault() returns the value of the item with the specified key
        for path in g:
            node1 = nodes.setdefault(path[0], Node(path[0]))
            node2 = nodes.setdefault(path[1], Node(path[1]))
            total += Union(node1, node2)
        weights.append(k)
        path_count.append(total)
    
    res = []
    for L, R in queries:
        Li = bisect(weights, L-1) - 1
        Ri = bisect(weights, R) - 1
        res.append(path_count[Ri] - path_count[Li])
    return res
    
    

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    n, q = map(int, input().split())
    tree = []

    for _ in range(n-1):
        tree.append(list(map(int, input().rstrip().split())))

    queries = []

    for _ in range(q):
        queries.append(list(map(int, input().rstrip().split())))

    result = solve(tree, queries)

    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
