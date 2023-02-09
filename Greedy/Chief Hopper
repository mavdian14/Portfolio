#!/bin/python3

import math
import os
import random
import re
import sys

def chiefHopper(arr):
    start_energy = 0
    while True:
        energy = start_energy
        for item in arr:
            energy = energy * 2 - item
            if energy < 0:
                break
        if energy >= 0:
            return start_energy
        start_energy += 1

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    result = chiefHopper(arr)

    fptr.write(str(result) + '\n')

    fptr.close()
