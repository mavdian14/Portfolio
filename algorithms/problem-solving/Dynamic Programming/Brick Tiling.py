#!/bin/python3

import math
import os
import random
import re
import sys

def memoize(func):
    pool = {}
    def wrapper(*arg):
        if arg not in pool:
            pool[arg] = func(*arg)
        return pool[arg]
    return wrapper

mod = 1000000007
shapes = (\
    ((1,0),(2,0),(2,1)),\
    ((0,1),(0,2),(-1,2)),\
    ((0,1),(1,1),(2,1)),\
    ((1,0),(0,1),(0,2)),\
    ((0,1),(-1,1),(-2,1)),\
    ((0,1),(0,2),(1,2)),\
    ((1,0),(2,0),(0,1)),\
    ((1,0),(1,1),(1,2)))

for case in range(int(input())):
    Y,X = map(int,input().split())
    mx = [int(''.join('0' if c =='.' else '1' for c in input().rstrip()), 2) for i in range(Y)]
    mx = mx + 3*[0]
    full = (1<<X)-1

    @memoize
    def rec(y,first,second,third):
        if y==Y:
            return 1 if first == second and second == third and third == 0 else 0
        if first == full:
            return rec(y+1,second,third,mx[y+3])

        def can_fit(rows,shape,x_offset):
            res = rows[:]
            for x,y in shape:
                x += x_offset
                if x < 0 or x >= X or y < 0 or y >= Y:
                    return None
                if res[y] & (1<<x) != 0:
                    return None
                res[y] |= (1<<x)
            return res

        free = 0
        while (first & (1<<free)) != 0:
            free += 1
        rows = [first | (1<<free),second,third]
        ans = 0
        for shape in shapes:
            nrows = can_fit(rows,shape,free)
            if nrows != None:
                ans = (ans + rec(y, *nrows)) % mod
        return ans

    print(rec(0,mx[0],mx[1],mx[2]))
