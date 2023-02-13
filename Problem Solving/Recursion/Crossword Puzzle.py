#!/bin/python3

import math
import os
import random
import re
import sys

def nextperm(p):
    last = len(p) -2
    while last >= 0 and p[last] > p[last + 1]:
        last -= 1
    if last < 0:
        return None
    end = len(p) -1
    while p[end] < p[last]:
        end -= 1
    p[last], p[end] = p[end], p[last]
    p[last+1:] = p[last+1:][::-1]
    return p

def check(crossword, slots, words):
    c = []
    for i in range(10):
        c.append(list(crossword[i]))
        
    for s,w in zip(slots, words):
        if s[2] == 'h':
            for i,v in enumerate(w):
                x,y = s[0],s[1]+i
                if c[x][y] == '-' or c[x][y] == v:
                    c[x][y] = v
                else:
                    return None
        if s[2] == 'v':
            for i,v in enumerate(w):
                x,y = s[0]+i,s[1]                
                if c[x][y] == '-' or c[x][y] == v:
                    c[x][y] = v
                else:
                    return None
    return [''.join(x) for x in c]
    
def crosswordPuzzle(crossword, words):
    # Write your code here
    # back track.
    slots = []    # (x,y,[h|v])
    for i,row in  enumerate(crossword):
        for j,c in enumerate(row):
            if c == '-':
                if (i == 0 or crossword[i-1][j] == '+') and i < 9 and crossword[i+1][j] == '-':
                    slots.append((i,j, 'v'))
                if (j == 0 or crossword[i][j-1] == '+') and j < 9 and crossword[i][j+1] == '-':
                    slots.append((i,j, 'h'))    
    words = words.split(';')
    indexpermuation = list(range(len(words)))
    while indexpermuation != None:
        checking = []
        for i in indexpermuation:
            checking.append(words[i])
        c = check(crossword, slots, checking)
        if c:
            return c
        indexpermuation = nextperm(indexpermuation)
    

if __name__ == '__main__':
    
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    crossword = []

    for _ in range(10):
        crossword_item = input()
        crossword.append(crossword_item)

    words = input()

    result = crosswordPuzzle(crossword, words)

    fptr.write('\n'.join(result))
    fptr.write('\n')

    fptr.close()
