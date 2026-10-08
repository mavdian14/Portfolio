#!/bin/python3

import math
import os
import random
import re
import sys
sys.setrecursionlimit(150000)
#
# Complete the 'componentsInGraph' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts 2D_INTEGER_ARRAY gb as parameter.
#
#need to do a depth-first search

def componentsInGraph(gb):
    #first build a graph
    graph = {}
    for l,r in gb:
        if l in graph:
            graph[l].add(r)
        else: graph[l] = {r}
        if r in graph:
            graph[r].add(l)
        else: graph[r] = {l}
    
    #find all nodes in each cluster & count the number of nodes
    
    visited = set()
    cluster = 0 #cluster index
    counter = [] # num of nodes in cluster
    
    for node in graph:
        if node not in visited:
            #if unvisited node, its a new cluster
            counter.append(0)
            #find all nodes in this cluster, start with current node
            stack = [node]
            while stack:
                #get next node in cluster
                n = stack.pop()
                if n not in visited:
                    counter[cluster] +=1
                    #mark node as visited
                    visited.add(n)
                    #add connected nodes to the stack
                    #.extend() adds all the elements of an iterable to the end of a list. .difference() returns a set containing the difference between 2 sets.
                    stack.extend(graph[n].difference(visited))
            #if node not visited, its a new cluster
            cluster +=1
    return [min(counter),max(counter)]
        

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    gb = []

    for _ in range(n):
        gb.append(list(map(int, input().rstrip().split())))

    result = componentsInGraph(gb)

    fptr.write(' '.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
