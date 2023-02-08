#!/bin/python3

import math
import os
import random
import re
import sys
from collections import deque
#
# Complete the 'bfs' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts following parameters:
#  1. INTEGER n
#  2. INTEGER m
#  3. 2D_INTEGER_ARRAY edges
#  4. INTEGER s
#

def bfs(n, m, edges, s):
    # create adjacency list for the graph
    graph = [[] for i in range(n+1)]
    for x,y in edges:
        #bidirectional graph
        graph[x].append(y)
        graph[y].append(x)
    
    visited = [False] * (n+1)
    #create distance list
    distances = [-1] * (n+1)
    #initialize the queue
    q = deque([(s,0)])
    #update value for starting node
    distances[s] = 0
    visited[s] = True
    
    #main logic
    while q:
        u,w = q.popleft()
        for v in graph[u]:
            if visited[v] == False:
                distances[v] = w+6
                visited[v] = True
                q.append((v,w+6))
    #remove starting node distance as it's not required in answer
    distances.remove(0)
    
    return distances[1:]
                
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    q = int(input().strip())

    for q_itr in range(q):
        first_multiple_input = input().rstrip().split()

        n = int(first_multiple_input[0])

        m = int(first_multiple_input[1])

        edges = []

        for _ in range(m):
            edges.append(list(map(int, input().rstrip().split())))

        s = int(input().strip())

        result = bfs(n, m, edges, s)

        fptr.write(' '.join(map(str, result)))
        fptr.write('\n')

    fptr.close()
