#!/bin/python3

import os
import sys

#
# Complete the indianJob function below.
#
T = int(input())
for t in range(T):
   N, G = map(int, input().split())
   A = [int(x) for x in input().split()]
   s = set([0])
   for x in A:
      for t in list(s):
         s.add(x + t)
   x = sum(A)
   for t in s:
      if t <= G and x - t <= G:
         print('YES')
         break
   else:
      print('NO')
