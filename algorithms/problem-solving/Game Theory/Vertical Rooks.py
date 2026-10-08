#!/bin/python3

import math
import os
import random
import re
import sys


def verticalRooks(r1, r2):
    xors = 0
    for y1,y2 in zip(r1,r2):
        xors ^= (abs(y1-y2)-1)
    return "player-2" if xors != 0 else "player-1"

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input())

    for t_itr in range(t):
        n = int(input())

        r1 = []

        for _ in range(n):
            r1_item = int(input())
            r1.append(r1_item)

        r2 = []

        for _ in range(n):
            r2_item = int(input())
            r2.append(r2_item)

        result = verticalRooks(r1, r2)

        fptr.write(result + '\n')

    fptr.close()
