#!/bin/python3

import math
import os
import random
import re
import sys

import heapq
sys.setrecursionlimit(100000)

def dfs(graph, start,dlength,EdgeDis):
    visited, stack = set(), [start]
    distances = [-1] * dlength
    distances[int(start) -1]=0
    
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            for v in graph[vertex]:
                if distances[int(v)-1]==-1:
                    distances[int(v)-1]=distances[int(vertex)-1]+min(EdgeDis[tuple([vertex,v])])
            stack.extend(graph[vertex] - visited)
    return [x for x in distances if x!=-1]

'''   
def bfs(graph, start,dlength,EdgeDis):
    visited, queue = set(), [start]
    distances = [-1] * dlength
    distances[int(start) -1]=0
    #print distances
    while queue:
        vertex = queue.pop(0)
        if vertex not in visited:
            visited.add(vertex)
            #print vertex
            for v in graph[vertex]:
                #print v,
                #if int(v)!=int(start):
                if distances[int(v)-1]==-1:
                    distances[int(v)-1]=distances[int(vertex)-1]+min(EdgeDis[tuple([vertex,v])])
            queue.extend(graph[vertex] - visited)
    #print distances,'*'*10,visited
    return filter(lambda x:x!=-1,distances)
'''    
'''
def djikstra(graph,start,n,EdgeDis):
    visited,hq=set(),[]
    distances=[-1]*n
    distances[start-1]=0
    heapq.heappush(hq,(distances[int(start) -1],start))    
    while len(hq)!=0:
        (dis,vertex)=heapq.heappop(hq) 
        if vertex not in visited:
            visited.add(vertex)
            if distances[vertex-1]==-1:
                distances[vertex-1]=dis
            for v in graph[vertex]:
                if distances[int(v)-1]==-1 or distances[int(v)-1] > dis+min(EdgeDis[tuple([vertex,v])]):
                    distances[int(v)-1]=dis+min(EdgeDis[tuple([vertex,v])]) 
                    heapq.heappush(hq,(distances[int(v)-1],int(v)))
    return distances
'''
n=int(eval(input()))
graph=dict()
EdgeDis=dict()
for r in range(n-1):
    a,b,c=list(map(int,input().split()))
    #make graph and EdgeDistances
    graph.setdefault(a,set()).add(b)
    graph.setdefault(b,set()).add(a)
    EdgeDis.setdefault(tuple([a,b]),list()).append(c)
    EdgeDis.setdefault(tuple([b,a]),list()).append(c)
#print graph 
#print EdgeDis
sol = dfs(graph,1,n,EdgeDis)
sol2 = dfs(graph,n,n,EdgeDis)
print((min(sum(sol), sum(sol2))))
#print min(sum([0 if k==-1 else int(k) for k in sol]) ,  sum([0 if k==-1 else int(k) for k in sol2]) )
#sol = ['-1' if k=='inf' else str(k) for k in sol]  
#print ' '.join(sol)
