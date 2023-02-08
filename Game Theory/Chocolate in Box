#!/bin/python3

import math
import os
import random
import re
import sys

n=int(input())
a=[int(x) for x in input().split(' ')]
xa=0
for x in a:
  xa^=x
turns=sum(1 for x in a if x^xa<x)
print(turns)
