#!/bin/python3

import os
import sys

def test(ours, theirs, x, y):
    if not (0 <= x <= 3 and 0 <= y <= 3):
        return -1, -1
    for nt in range(len(theirs)):
        mm, xx, yy = theirs[nt]
        if mm != ' ' and xx == x and yy == y:
            return (2 if mm == 'Q' else 1), nt
    for mm, xx, yy in ours:
        if mm != ' ' and xx == x and yy == y:
            return -1, -1
    return 0, -1
  
#moves of a knight
dn = [(-1, -2), (-2, -1), (-1, 2), (-2, 1), (1, -2), (2, -1), (1, 2), (2, 1)]
#moves of a rook
dr = [(-1, 0), (1, 0), (0, -1), (0, 1)]
#moves of a bishop
db = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
#moves a queen
dq = dr + db

def gen(ours, theirs, xx, yy, d):
    if d == dn:
        for dx, dy in d:
            x, y = xx + dx, yy + dy
            t, nt = test(ours, theirs, x, y)
            if t >= 0:
                yield x, y, t, nt
    else:
        for dx, dy in d:
            x, y = xx, yy
            while True:
                x, y = x + dx, y + dy
                t, nt = test(ours, theirs, x, y)
                if t < 0:
                    break
                yield x, y, t, nt
                if t > 0:
                    break

men = {'N': dn, 'B': db, 'R': dr, 'Q': dq}

def solve(ours, theirs, moves):
    result = -2
    for no in range(len(ours)):
        mm, xx, yy = ours[no]
        if mm != ' ':
            for x, y, t, nt in gen(ours, theirs, xx, yy, men[mm]):
                if t == 2:
                    return 1
                if moves > 1:
                    if nt >= 0:
                        old = theirs[nt][0]
                        theirs[nt][0] = ' '
                    ours[no][1:] = [x, y]
                    rr = -solve(theirs, ours, moves - 1)
                    if nt >= 0:
                        theirs[nt][0] = old
                    ours[no][1:] = [xx, yy]
                    result = max(rr, result)
                    if result == 1:
                        return 1
    return 0 if result == -2 else result


def simplifiedChessEngine(whites, blacks, moves):
    if moves % 2 == 0:
        moves -= 1
    for a in [whites, blacks]:
        for b in a:
            b[1] = ord(b[1]) - ord('A')
            b[2] = ord(b[2]) - ord('1')
    return 'YES' if solve(whites, blacks, moves) == 1 else 'NO'

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    g = int(input())

    for g_itr in range(g):
        wbm = input().split()

        w = int(wbm[0])

        b = int(wbm[1])

        m = int(wbm[2])

        whites = []

        for _ in range(w):
            whites.append(list(map(lambda x: x[0], input().rstrip().split())))

        blacks = []

        for _ in range(b):
            blacks.append(list(map(lambda x: x[0], input().rstrip().split())))

        result = simplifiedChessEngine(whites, blacks, m)
        fptr.write(result + '\n')

    fptr.close()
