#!/bin/python3

import math
import os
import random
import re
import sys

vertices = int(input())
graph = [[], [], [], []]
count = 0
G1 = 1
G2 = 2
G3 = 3

for i in range(1, 4):
    for j in range(0, vertices + 1):
        graph[i].append(None)

for i in range(1, 4):
    edges = int(input())
    for j in range(0, edges):
        edge = list(map(int, input().split(" ")))
        if graph[i][edge[0]] is None:
            graph[i][edge[0]] = set()
        graph[i][edge[0]].add(edge[1])
        if graph[i][edge[1]] is None:
            graph[i][edge[1]] = set()
        graph[i][edge[1]].add(edge[0])

for vertex in range(1, vertices + 1):
    verticesToG1 = graph[G1][vertex]
    if verticesToG1 is not None:
        verticesFromG2 = graph[G2][vertex]
        if verticesFromG2 is not None:
            for toVertex in verticesFromG2:
                verticesFromG3 = graph[G3][toVertex]
                if verticesFromG3 is not None:
                    count = count + len(verticesToG1.intersection(verticesFromG3))
        
print(count)
