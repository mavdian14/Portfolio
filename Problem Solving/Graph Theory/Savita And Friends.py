#!/bin/python3

import math
import os
import random
import re
import sys

import heapq
def calc_dist(G, start):
   dist = [-1] * len(G)
   active = [(0, start)]
   while active:
      d, i = heapq.heappop(active)
      if dist[i] >= 0: continue
      dist[i] = d
      for j, e in G[i]:
         if dist[j] < 0:
            heapq.heappush(active, (d+e, j))
   return dist

T = int(input())
for t in range(T):
   N, M, K = map(int, input().split())
   edges = []
   G = [[] for i in range(N+1)]
   for i in range(M):
      A, B, C = map(int, input().split())
      edges.append((A, B, C))
      G[A].append((B, C))
      G[B].append((A, C))
   A, B, C = edges[K-1]
   distA = calc_dist(G, A)
   distB = calc_dist(G, B)
   peaks = []
   for i in range(1,N+1):
      x = (C + distB[i] - distA[i]) / 2
      peaks.append((x, distA[i] + x))
   peaks.sort()
   pts = []
   for x, y in peaks:
      while pts:
         x0, y0 = pts[-1]
         if y0 > y - x + x0: break
         pts.pop()
      if pts:
         x0, y0 = pts[-1]
         xy = x0 + y0
         if y > xy - x:
            x1 = (xy - y + x) / 2
            pts.append((x1, xy - x1))
            pts.append((x, y))
      else:
         if x > 0:
            pts.append((0, y - x))
         pts.append((x, y))
   x, y = pts[-1]
   if x < C: pts.append((C, y + x - C))
   xmin, ymin = pts[0]
   for x, y in pts:
      if y < ymin:
         xmin = x
         ymin = y
   print("%.5f %.5f" % (xmin, ymin))
