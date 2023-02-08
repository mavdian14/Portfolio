#!/bin/python3

import math
import os
import random
import re
import sys
import copy

N, M = (int(i) for i in input().split())

def add_to_graph(graph, edge):
  start, end = edge
  if start not in graph:
    graph[start] = {}
  if end not in graph[start]:
    graph[start][end] = 1
  else:
    graph[start][end] += 1

def print_graph(graph):
  for i in sorted(graph.keys(), key=int):
    print(i, ":", *list(graph[i].keys()))

graph = {}
backward_graph = {}
for line in sys.stdin:
  edge = tuple(int(i) for i in line.split())
  add_to_graph(graph, edge)
  add_to_graph(backward_graph, reversed(edge))

def find_reachable(start, graph):
  reachable = set()
  working = {start}
  while working:
    reachable.update(working)
    next_working = set()
    for node in working:
      if node not in graph:
        continue
      next_working.update({adj for adj in graph[node].keys()
                           if adj not in reachable})
    working = next_working
  return reachable

def purge_unreachable(graph, reachable):
  for start in list(graph.keys()):
    if start not in reachable:
      del graph[start]
    else:
      for end in list(graph[start].keys()):
        if end not in reachable:
          del graph[start][end]

forward_reachable = find_reachable(1, graph)
backward_reachable = find_reachable(N, backward_graph)
reachable = forward_reachable.intersection(backward_reachable)

purge_unreachable(graph, reachable)
purge_unreachable(backward_graph, reachable)

# check for loops -- Kosaraju's algorithm
# http://en.wikipedia.org/wiki/Kosaraju%27s_algorithm
class Pop:
  def __repr__(self): return "pop"
pop_token = Pop()
seen = set()
dfs_stack = [1]
visited_stack = []
# Do a depth first search originating from the first node, and
# push nodes onto the visited_stack in the order the search
# visits them. Keep track of seen nodes, avoiding repeats.
while dfs_stack:
  cur = dfs_stack[-1]
  if cur == pop_token:
    dfs_stack.pop()
    visiting_node = dfs_stack.pop()
    visited_stack.append(visiting_node)
    continue
  if cur in seen:
    dfs_stack.pop()
    continue
  seen.add(cur)
  dfs_stack.append(pop_token)
  if cur not in graph:
    continue
  for child in graph[cur].keys():
    if child in seen:
      continue
    dfs_stack.append(child)
# The visited stack now contains all nodes. Pop out each of them
# in reverse order. For each, see if it can reach any nodes in
# the backwards graph. If so, you have a cycle! If not, remove it
# from the backwards graph and continue.
backward_graph_copy = copy.deepcopy(backward_graph)
while visited_stack:
  cur = visited_stack.pop()
  if cur in backward_graph_copy:
    print("INFINITE PATHS")
    exit()
  if cur in graph:
    for node in graph[cur]:
      del backward_graph_copy[node][cur]
      if len(backward_graph_copy[node]) == 0:
        del backward_graph_copy[node]

# Count the paths to each node. Paths can't propagate out of node
# until all the paths to that node have been counted.  Thus we
# track visits and compare against the backwards graph, to see
# when a node is ready to move forward.
working = {1}
weights = {1:1}
visits = {}
while working:
  new_working = set()
  for node in working:
    if node not in graph:
      continue
    for (adj, count) in graph[node].items():
      if adj not in weights:
        weights[adj] = 0
      weights[adj] += weights[node] * count
      if adj not in visits:
        visits[adj] = 0
      visits[adj] += 1
      if visits[adj] == len(backward_graph[adj]):
        new_working.add(adj)
  working = new_working

answer = weights[N]
print(answer % (10**9))
