#!/bin/python3

import math
import os
import random
import re
import sys

def Find( uf, u ):
    if uf[ u ] != u:
        uf[ u ] = Find( uf, uf[ u ])
    return uf[ u ]

def Sol( E, mlocs, N ):
    uf = list(range(N))
    E = sorted(E)
    res = 0#MaxST = set()
    while E:
        w,u,v = E.pop()
        #print(w,u,v, uf, mlocs)
        if Find( uf, u ) in mlocs and Find( uf, v ) in mlocs: res += w; continue
        if random.randint(0,1):
            if Find( uf, u ) in mlocs: mlocs.add( Find( uf, v ) )
            uf[ Find( uf, u ) ] = Find( uf, v )            
        else:
            if Find( uf, v ) in mlocs: mlocs.add( Find( uf, u ) )
            uf[ Find( uf, v ) ] = Find( uf, u )            
        #MaxST.add( (w,u,v) )
    return res
        
    

N, K = map(int, input().split())
E = set()
mlocs = set()
for _ in range(N-1):
    u,v,w = map(int,input().split())
    E.add( (w, u, v) )
for _ in range(K):
    u = int(input())
    mlocs.add( u )
    
print( Sol( E, mlocs, N ))
#print(mlocs, E)
