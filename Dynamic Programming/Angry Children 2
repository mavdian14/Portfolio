#!/bin/python3

import math
import os
import random
import re
import sys

# Elements are sorted
# x[k - 1] is larger than all other k - 1 elements,
# it occurs with a factor of (k - 1)
# x[k - 2] is larger than k - 2 elements but smaller than one
# it occurs with a factor of +(k - 2) and -1

# So in general, i occurs with a factor of +i and -(k - 1 - i)
def calc_angry_val(arr, start, k):
    angry_val = 0
    for i in range(k):
        angry_val = angry_val + nrs[start + i] * i - nrs[start + i] * (k - 1 - i)
    return angry_val

n = int(input())
k = int(input())

nrs = sorted(int(input()) for _ in range(n))

sums = [0] * (n + 1)
for i in range(n):
    sums[i + 1] = sums[i] + nrs[i]

# Let's select the first block of k candies and compute the angry_val
angry_val = calc_angry_val(nrs, 0, k)
result = angry_val

# Now if we proceed, shifting out the left value x_left removes (k - 1) * x_left
# And shifting in the new value x_right adds (k - 1) * x_right
for i in range(k, n):
    angry_val += (k - 1)  * nrs[i - k]
    angry_val += (k - 1)  * nrs[i]
    angry_val -= 2 * (sums[i] - sums[i - k + 1])
    result = min(result, angry_val)

print(result)
