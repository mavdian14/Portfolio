#!/bin/python3

import math
import os
import random
import re
import sys

def grow(n):
  res = 0
  for i in range(1, n):
    res += i*(i+1)
    #print("-->", i, res)
  return res
  
def mark(x):
  z = x
  while z: z = z[0]
  if x is not z: x[0] = z
  return z

def mark2(x):
  z = x
  while z and type(z) == list: z = z[0]
  if x is not z: x[0] = z
  return z

  
T = int(input())
for t in range(T):
  n, m = map(int, input().split())
  work = [[] for i in range(n)] 
  lost = 0
  for i in range(m):
    u, v = map(int, input().split())
    u -= 1
    v -= 1
    mu = mark(work[u])
    mv = mark(work[v])
    if mu is not mv:
      mu.append(mv)
    else:
      lost += 1
      
  no = 1
  dic = {}
  for i in range(n):
    z = mark2(work[i])
    if not z:
      z.append(no)
      z = no
      no += 1
      dic[z] = 1
    else:
      dic[z] += 1

  res = 0
  cur = 0    
  for v in sorted(dic.values(), reverse = True):
    res += grow(v) + (v-1) * cur
    cur += v*(v-1)
    #print(v, cur, res) 
    
  res += lost * cur
  print(res)
