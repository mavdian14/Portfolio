#!/bin/python3

import math
import os
import random
import re
import sys

INFINITY = 0xFFFFFFFF
class vertex:
    def __init__(self):
        self.adj = {}

def bellman_ford(V, s, sp):
    sp[s][s] = 0
    sps = sp[s]
    for i in range(0,len(V)):
        done = True
        for x in range(0, len(V)):
            for y in V[x].adj.keys():
                w = V[x].adj[y]
                if sps[y] > sps[x]+w:
                    sps[y] = sps[x]+w
                    done = False
        if done == True:
            break
        
        
var = input().split()
N,M = int(var[0]),int(var[1])

SP_done = [INFINITY]*N    #Indicates if we have ran SP from a specific source
V = []   #List of vertices
V = [vertex() for i in range(0,N)]
SP = [[INFINITY for i in range(0,N)] for i in range(0,N)]

for i in range(0,M):
    var = input().split()
    x,y,w = int(var[0]), int(var[1]), int(var[2])
    x= x-1
    y= y-1
    V[x].adj[y] = w

T = int(input())
out=""
for t in range(0,T):
    var = input().split()
    x,y = int(var[0]) , int(var[1])
    x = x-1
    y = y-1
    if SP_done[x] != 0:
        SP_done[x] = 0
        bellman_ford(V, x, SP)
        
    if SP[x][y] == INFINITY:
        out += "{}\n".format(-1)
    else:
        out += "{}\n".format(SP[x][y])
print(out)
#print(SP)
