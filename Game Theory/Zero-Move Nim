#!/bin/python3

import math
import os
import random
import re
import sys

test_case = int(input())

for temp_test_case in range(test_case):
    n = int(input())
    s = input()
    a = [int(elem) for elem in s.split() ]
    
    # print (a)
    
    x = 0
    for i in a:
        if i == 0:
            continue
        if i % 2 == 0:
            x = x ^ (i-1)
        else:
            x = x ^ ( i + 1)

    # print(x)

    if x != 0:
        print('W')
    else:
        print('L')
