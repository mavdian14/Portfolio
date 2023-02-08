#!/bin/python3

import math
import os
import random
import re
import sys
from collections import deque

debug = False

def show(matrix):
  if False:
    for row in matrix:
      print(str(row))

def cost(r,b):
  dx = b[0]-r[0]
  dy = b[1]-r[1]
  return dx*dx+dy*dy

def check(limit): # can we connect k riders to k bicycles with only segments less than limit?
  rtob = {r: [b for b in range(m) if c[r][b] <= limit] for r in range(n)}
  btor = {b: [r for r in range(m) if c[r][b] <= limit] for b in range(m)}
  # assign as many as we can, stop if we can get to k of them
  assd_r = {}
  assd_b = {}
  assd = 0
  arb = False
  assdnow = True
  while assdnow:
    if debug:
      print("Looping through")
    assdnow = False
    for r in range(n):
      if r not in assd_r:
        # node isn't assigned yet; try and find an augmenting path (DFS)
        # leads from this r to any unassigned b, possibly going through current assignations
        paths = deque() # contains candidate augmenting paths
        visited_r = set()
        visited_r.add(r)
        for b in reversed(rtob[r]):
          paths.append([(r,b)])
        while paths:
          path = paths.pop()
          rc, b = path[-1] # last tuple, try and expand from here
          # candidate: rc -> b
          if b not in assd_b:
            # b isn't assigned; this is an augmenting path
            if debug:
              print("assigning", path)
            for rc, b in path:
              assd_r[rc] = b
              assd_b[b] = rc
            assd += 1
            if assd >= k:
              if debug:
                print("Success! Assigned %d nodes of %d"%(assd,k))
              return True
            assdnow = True
            break # augmenting path found
          else: # b is assigned; follow the assigment back to an r (but not the same one) and try again
            if debug:
              print("continuing", path)
            rc = assd_b[b]
            if rc not in visited_r:
              visited_r.add(rc)
              for bc in reversed(rtob[rc]):
                if b != bc:
                  np = path[:]
                  np.append((rc,bc))
                  paths.append(np)
  if debug:
    print("Failure! Assigned %d nodes of %d"%(assd,k))
  return False

n,m,k = map(int,input().split())
rs = [tuple(map(int,input().split())) for _ in range(n)] # riders
bs = [tuple(map(int,input().split())) for _ in range(m)] # bicycles
c = [[cost(r,b) for b in bs] for r in rs] # adjacency graph - dense
show(c)
segs = sorted([c[r][b] for r in range(n) for b in range(m)])
# binary search using check function
lo = 0
hi = len(segs) - 1
while lo < hi:
  # invariant: smallest to succeed is x | lo <= x <= hi
  mid = (hi + lo) // 2
  if debug:
    print("examining (%d,%d,%d) (%d)"%(lo,mid,hi,segs[mid]))
  if check(segs[mid]):
    # succeeded, make mid highest in range (keep it since it might be target)
    hi = mid
  else:
    # failed, try more edges (mid can't be target)
    lo = mid + 1
# lo <- smallest to succeed
print(segs[lo])
