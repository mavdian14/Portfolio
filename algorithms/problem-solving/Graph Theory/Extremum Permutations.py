#!/bin/python3

import math
import os
import random
import re
import sys

from itertools import islice, accumulate

MOD = 10**9 + 7
# elements b_i are greater than their adjacent elements, whereas a_i are less than their adjacent elements
def permcount(permlen, a, b):
    if any(x+1 == y for c in map(sorted, (a, b)) for x, y in zip(c, c[1:])):
        return 0
    if set(a) & set(b):
        return 0
    goingup = [None] * permlen
    for c, low in ((a, True), (b, False)):
        for elt in c:
            elt -= 1
            if elt > 0:
                goingup[elt] = not low
            if elt < permlen - 1:
                goingup[elt+1] = low
    count = [1]
    #Return an iterator whose next() method returns selected values from an iterable. If start is specified, will skip all preceding elements; otherwise, start defaults to zero. Step defaults to one. If specified as another value, step determines how many values are skipped between successive calls. 
    for i, inc in islice(enumerate(goingup), 1, permlen):
        if inc is None:
            count = [sum(count)] * (i+1)
        elif inc:
            #Return series of accumulated sums (or other binary function results).
            count = [0] + list(accumulate(count))
        else:
            count = list(reversed(list(accumulate(reversed(count))))) + [0]
        count = [elt % MOD for elt in count]
    return sum(count) % MOD
    

def readints():
    return [int(f) for f in input().split()]

permlen, alen, blen = readints()
a = readints()
b = readints()
assert len(a) == alen and len(b) == blen
print(permcount(permlen, a, b))
