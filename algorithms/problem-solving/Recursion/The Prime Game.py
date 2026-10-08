#!/bin/python3

import math
import os
import random
import re
import sys

# 2, 3, 5, 7, 11, 13
values = [0, 0, 1, 1, 2, 2, 3, 3, 4]
    
def winner(A):
    nimber = 0  # or grundy number  
    for ak in A:
        nimber ^= values[ak % len(values)];

    return "Manasa" if nimber > 0 else "Sandy"

for _ in range(int(input())):
    input(), print(winner(list(map(int, input().split()))))
