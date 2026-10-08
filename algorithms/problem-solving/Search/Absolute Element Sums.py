#!/bin/python3

import math
import os
import random
import re
import sys

from collections import Counter

def q(arr, queries):
    positive_n = [el for el in arr if el >= 0]
    negative_n = [el for el in arr if el <  0]
    pos_size = len(positive_n)
    neg_size = len(negative_n)
    positive = list(reversed(sorted(Counter(positive_n).items())))
    negative = sorted(Counter(negative_n).items())
    tot = sum(abs(el) for el in arr)
    diff = 0  # cum sum of queries
    for q in queries:
        diff += q
        tot += pos_size * q - neg_size * q
        if q > 0:
            while neg_size and negative[-1][0] + diff >= 0:
                (n, count) = negative.pop()
                positive.append((n, count))
                pos_size += count
                neg_size -= count
                tot += abs(n + diff) * 2 * count
        else:
            while pos_size and positive[-1][0] + diff < 0:
                (n, count) = positive.pop()
                negative.append((n, count))
                neg_size += count
                pos_size -= count
                tot += abs(n + diff) * 2 * count
        yield tot

input()
arr = [int(s) for s in input().split()]

input()
que = [int(s) for s in input().split()]

for res in q(arr, que):
    print(res)
