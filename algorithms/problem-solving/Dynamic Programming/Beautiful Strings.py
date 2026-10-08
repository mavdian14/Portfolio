#!/bin/python3

import math
import os
import random
import re
import sys
import itertools

s = input()
# make an iterator that returns consecutive keys and groups from the iterable. If the key function is not specified or is None, the element itself is used for grouping.
groups = [(c, sum(1 for x in l)) for c, l in itertools.groupby(s)]
multiple = sum(x[1] > 1 for x in groups)
fence = sum(groups[i - 1][0] == groups[i + 1][0] and groups[i][1] == 1 \
            for i in range(1, len(groups) - 1))
print(multiple + len(groups) * (len(groups) - 1) // 2 - fence)
