#!/bin/python3

import os
import sys

def farthest_node_from_start(nodes,is_goal,subtree,starting_node):
    visited=[False for _ in nodes]
    st=[(0,starting_node)]
    visited[starting_node]=True
    largest = 0,starting_node
    all_dist_sum = 0
    while st:
        dist,u=st.pop()
        for v,d in nodes[u]:
            if not visited[v] and subtree[v]:
                elm=dist+d,v
                all_dist_sum+=d
                if is_goal[v]:
                    largest=max(largest,elm)
                st.append(elm)
                visited[v]=True
    return all_dist_sum,largest

def make_subtree(nodes,is_goal,starting_node):
    subtree=is_goal[:]
    for u,v in dfs(nodes, starting_node):
        subtree[u]=subtree[u] or subtree[v]
    return subtree

def dfs(nodes, starting_node):
    stack = [(starting_node, v) for v,d in nodes[starting_node]]
    edges = list()
    while stack:
        u, v = stack.pop()
        edges.append((u, v))
        stack.extend((v, w) for w,d in nodes[v] if w != u)
    edges.reverse()
    return edges

N, K = list(map(int,input().strip().split()))
goals = list(map(int,input().strip().split()))
is_goal=[False]*(N+1)

for item in goals:
    is_goal[item]=True
    
nodes=[[] for _ in range(N+1)]

for _ in range(N-1):
    u,v,d = list(map(int,input().strip().split()))
    nodes[u].append((v,d))
    nodes[v].append((u,d))

subtree = make_subtree(nodes,is_goal,goals[0])
a,(b,c)=farthest_node_from_start(nodes,is_goal,subtree,goals[0])
Distance,(d,_)=farthest_node_from_start(nodes,is_goal,subtree,c)
print(2*Distance-d)
