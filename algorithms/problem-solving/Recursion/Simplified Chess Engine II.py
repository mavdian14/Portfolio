#!/bin/python3

import math
import os
import random
import re
import sys

def validmoves(piece,posx,posy,whites,blacks,b):
    if piece=="R":
        L=[]
        i=1
        while posx+i<4 and not (posx+i,posy) in whites:
            L+=[("R",posx+i,posy)]
            if (posx+i,posy) in blacks:
                break
            i+=1
        i=1
        while posx-i>=0 and not (posx-i,posy) in whites:
            L+=[("R",posx-i,posy)]
            if (posx-i,posy) in blacks:
                break
            i+=1
        i=1
        while posy+i<4 and not (posx,posy+i) in whites:
            L+=[("R",posx,posy+i)]
            if (posx,posy+i) in blacks:
                break
            i+=1
        i=1
        while posy-i>=0 and not (posx,posy-i) in whites:
            L+=[("R",posx,posy-i)]
            if (posx,posy-i) in blacks:
                break
            i+=1
        return(L)
    elif piece=="B":
        L=[]
        i=1
        while posx+i<4 and posy+i<4 and not (posx+i,posy+i) in whites:
            L+=[("B",posx+i,posy+i)]
            if (posx+i,posy+i) in blacks:
                break
            i+=1
        i=1
        while posx-i>=0 and posy+i<4 and not (posx-i,posy+i) in whites:
            L+=[("B",posx-i,posy+i)]
            if (posx-i,posy+i) in blacks:
                break
            i+=1
        i=1
        while posx+i<4 and posy-i>=0 and not (posx+i,posy-i) in whites:
            L+=[("B",posx+i,posy-i)]
            if (posx+i,posy-i) in blacks:
                break
            i+=1
        i=1
        while posx-i>=0 and posy-i>=0 and not (posx-i,posy-i) in whites:
            L+=[("B",posx-i,posy-i)]
            if (posx-i,posy-i) in blacks:
                break
            i+=1
        return(L)
    elif piece=="Q":
        return([("Q",z[1],z[2]) for z in validmoves("R",posx,posy,whites,blacks,b)+validmoves("B",posx,posy,whites,blacks,b)])
    elif piece=="N":
        return([("N",z[0],z[1]) for z in [(posx+2,posy+1),(posx+2,posy-1),(posx+1,posy+2),(posx+1,posy-2),(posx-1,posy+2),(posx-1,posy-2),(posx-2,posy+1),(posx-2,posy-1)] if not z in whites and 0<=z[0]<=3 and 0<=z[1]<=3])
    elif piece=="P":
        posy+=1-2*b
        l=[]
        for i in [-1,1]:
            if 0<=posx+i<=3 and (posx+i,posy) in blacks:
                l+=[(posx+i,posy)]
        if not (posx,posy) in whites+blacks:
            l+=[(posx,posy)]
        if posy in [0,3]:
            return([("N",x[0],x[1]) for x in l]+[("B",x[0],x[1]) for x in l]+[("R",x[0],x[1]) for x in l])
        else:
            return([("P",x[0],x[1]) for x in l])

def simplifiedChessEngine(whites, blacks, moves,b):
    if moves==0:
        if b:
            return("YES")
        else:
            return("NO")
    else:
        wh=[(x[1],x[2]) for x in whites]
        bl=[(x[1],x[2]) for x in blacks]
        i,j=[z[1:] for z in blacks if z[0]=="Q"][0]
        l=sum([validmoves(x[0],x[1],x[2],wh,bl,b) for x in whites],[])
        if (i,j) in [x[1:] for x in l]:
            return("YES")
        else:
            nextmove=[];nextmove2=[]
            for i in range(len(whites)):
                for t in validmoves(whites[i][0],whites[i][1],whites[i][2],wh,bl,b):
                    if (t[1],t[2]) in bl:
                        nextmove.append((i,t))
                    else:
                        nextmove2.append((i,t))
            for x in nextmove+nextmove2:
                i,t=x[0],x[1]            
                piece,posx,posy=whites[i]
                taken=[z for z in blacks if (z[1],z[2])==t[1:]]
                blacks=[z for z in blacks if not z in taken]
                whites[i]=t
                if simplifiedChessEngine(blacks,whites,moves-1,1-b)=="NO":
                    whites[i]=(piece,posx,posy)
                    blacks+=taken
                    return("YES")
                else:
                    whites[i]=(piece,posx,posy)
                    blacks+=taken
            return("NO")

if __name__ == '__main__':
    g = int(input())

    for g_itr in range(g):
        wbm = input().split()

        w = int(wbm[0])

        b = int(wbm[1])

        m = int(wbm[2])

        whites = []

        for _ in range(w):
            whites.append(input().rstrip().split())

        blacks = []

        for _ in range(b):
            blacks.append(input().rstrip().split())
        
        whites=[[x[0],ord(x[1])-65,int(x[2])-1] for x in whites]
        blacks=[[x[0],ord(x[1])-65,int(x[2])-1] for x in blacks]

        result = simplifiedChessEngine(whites, blacks, m,0)
        print(result)
        # Write Your Code Here
