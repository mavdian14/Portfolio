#!/bin/python3

import math
import os
import random
import re
import sys

p = []
prime = 1000000007
q = sys.stdin.readline().split()
n = int(q[0])
k = int(q[1])
minx = 100000
maxx = 0
miny = 100000
maxy = 0

for i in range(n):
    w = sys.stdin.readline().split()
    a = int(w[0])
    b = int(w[1])
    p.append((a, b))
    minx = min(a, minx)
    maxx = max(a, maxx)
    miny = min(b, miny)
    maxy = max(b, maxy)

def ext_euclid(a, b):
    if b == 0:
        return 1, 0
    x, y = ext_euclid(b, a % b)
    return (y, x - a // b * y)

def comp(n, k):
    if k < 0 or n < k:
        return 0
    if n - k < k:
        k = n - k
    result = 1
    for t in range(n - k + 1, n + 1):
        result = result * t % prime
    divide = 1
    for t in range(1, k + 1):
        divide = divide * t % prime
    u = ext_euclid(prime, divide)[1]
    while (u < 0):
        u += prime
    result = result * u % prime
    return result

def checker(p, x0, x1, y0, y1):
    return p[0] == x0 or p[0] == x1 or p[1] == y0 or p[1] == y1

def counter(x0, x1, y0, y1):
    result = 0
    for i in range(n):
        if checker(p[i], x0, x1, y0, y1):
            result += 1
    return result

answer = 0

# left
m = counter(-1, -1, miny, -1)
answer = answer + comp(n - m, k - m)

# right
m = counter(-1, -1, -1, maxy)
answer = answer + comp(n - m, k - m)

# up
m = counter(minx, -1, -1, -1)
answer = answer + comp(n - m, k - m)

# down
m = counter(-1, maxx, -1, -1)
answer = answer + comp(n - m, k - m)

# left + right
m = counter(-1, -1, miny, maxy)
answer = answer - comp(n - m, k - m)

# left + up
m = counter(minx, -1, miny, -1)
answer = answer - comp(n - m, k - m)

# left + down
m = counter(-1, maxx, miny, -1)
answer = answer - comp(n - m, k - m)

# right + up
m = counter(minx, -1, -1, maxy)
answer = answer - comp(n - m, k - m)

# right + down
m = counter(-1, maxx, -1, maxy)
answer = answer - comp(n - m, k - m)

# up + down
m = counter(minx, maxx, -1, -1)
answer = answer - comp(n - m, k - m)

# left + right + up
m = counter(minx, -1, miny, maxy)
answer = answer + comp(n - m, k - m)

# left + right + down
m = counter(-1, maxx, miny, maxy)
answer = answer + comp(n - m, k - m)

# left + up + down
m = counter(minx, maxx, miny, -1)
answer = answer + comp(n - m, k - m)

# right + up + down
m = counter(minx, maxx, -1, maxy)
answer = answer + comp(n - m, k - m)

# all
m = counter(minx, maxx, miny, maxy)
answer = answer - comp(n - m, k - m)

while answer < 0:
    answer += prime
print(answer % prime)
