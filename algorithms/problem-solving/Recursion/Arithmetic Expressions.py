#!/bin/python3

import math
import os
import random
import re
import sys

n=int(input())
elems=[int(x) for x in input().split(' ')]
ops=[None]*101
ops[elems[0]]=''
for e in elems[1:]:
  nops=[None]*101
  for (k,s) in enumerate(ops):
    if s==None:
      continue
    nops[(k+e)%101]=s+'+'
    nops[(k-e)%101]=s+'-'
    nops[(k*e)%101]=s+'*'
  ops=nops
r=str(elems[0])
for (k,s) in enumerate(ops[0]):
  r+=s+str(elems[k+1])
print(r)
