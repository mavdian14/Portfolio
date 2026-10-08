#!/bin/python3

import math
import os
import random
import re
import sys

data = sys.stdin.readlines()
T = int(data[0])


def run_game(N, a, b):
    c = [a[i] + b[i] for i in range(N)]  # a-b
    cs = [i for i, x in sorted(
        enumerate(c), key=(lambda y : y[1]))] # keys that sort c

    # Play game
    p1, p2 = (0, 0)  # payoffs to the two players
    for i in range(N):
        if (i % 2)==0:  # P1's turn
            p1 += a[cs.pop(-1)]
        else:  # P2's turn
            p2 += b[cs.pop(-1)]

    # Print results
    if p1 > p2:
        print("First")
    elif p1==p2:
        print("Tie")
    else:
        print("Second")
        

for k in range(T):
    N = int(data[3*k + 1])
    a = list(map(int, data[3*k + 2].split()))
    b = list(map(int, data[3*k + 3].split()))
    run_game(N, a, b)
