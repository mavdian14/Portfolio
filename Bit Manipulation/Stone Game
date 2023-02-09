#!/bin/python3

import math
import os
import random
import re
import sys

import operator as op
import functools as ft
from sys import stderr
MOD = 1000000007

def readcase():
    npiles = int(input())
    piles = [int(fld) for fld in input().split()]
    assert npiles == len(piles)
    return piles

def numsolns(piles):
    return (numunrestrictedsolns(piles) - 
            numunrestrictedsolns([pile-1 for pile in piles if pile > 1])) % MOD

def numunrestrictedsolns(piles, MOD=MOD):
    if len(piles) == 0:
        return 1
    xorall = ft.reduce(op.xor, piles)
    leftmost = ft.reduce(op.or_, piles).bit_length() - 1
    rightmost = max(0, xorall.bit_length() - 1)
    ans = 0
    for first1 in range(rightmost, leftmost+1):
        premult = 1
        matchbit = 1 << first1
        for i, bigalt in enumerate(piles):
            if bigalt & matchbit != 0:
                even = 1
                odd = 0
                for pile in piles[i+1:]:
                    neweven = (1 + (pile & ~-matchbit)) * even
                    newodd = (1 + (pile & ~-matchbit)) * odd
                    if pile & matchbit != 0:
                        neweven += matchbit * odd
                        newodd += matchbit * even
                    even, odd = neweven % MOD, newodd % MOD
                ans += (even if xorall & matchbit != 0 else odd) * premult % MOD
            premult = (premult * ((bigalt & ~-matchbit) + 1)) % MOD
    if xorall == 0:
        ans += 1
    return ans % MOD

print(numsolns(readcase()))
