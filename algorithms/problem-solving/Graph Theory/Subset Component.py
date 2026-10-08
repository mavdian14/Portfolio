#!/bin/python3

import math
import os
import random
import re
import sys
from functools import reduce
from operator import or_

def get_integers():
    from sys import stdin
    return int(stdin.readline().strip()), sorted(map(int, stdin.readline().strip().split()))

def dec(s):
    #{:b}.format(s) formats string s into a binary
    return '{:b}'.format(s).count('1')-1 if s else 0

def compute(head, *tail):
    hc = dec(head)
    if tail:
        #to tell that tail is a packing argument
        last, d = compute(*tail)
        #print('->', last, d)
        new = []
        d_ = d
        for k,v in last:
            if all(t&head==0 for t in k):
                x = v+hc
                d_ += x
                new.append((k+(head,), x))
            else:
                A = tuple(t for t in k if t&head==0)
                b = reduce(or_, (t for t in k if t&head!=0), head)
                #print('A', A)
                #print('b', b)
                x = dec(sum(A)+b)-len(A)
                d_ += x
                new.append((A+(b,), x))
        new_ = new + last
        #print('<-', new_, d_)
        return new_, d_
    else:
        return [((),0), ((head,), hc)], hc

n, I = get_integers()
print(64*2**n - compute(*I)[1])
