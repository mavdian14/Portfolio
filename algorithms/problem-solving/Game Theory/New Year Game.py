#!/bin/python3

import math
import os
import random
import re
import sys

def dis_winner(arr):
    arr = [x % 3 for x in arr]
    arr = filter(lambda k: k != 0, arr)
    freq = {1: 0, 2: 0}
    for i in arr:
        freq[i] += 1
    if freq[1] % 2 == 0 and freq[2] % 2 == 0:
        print('Koca')
    else:
        print('Balsa')

def main():
    num_tests = int(input())
    for test in range(num_tests):
        size = int(input())
        arr = [int(x) for x in input().split(' ')]
        dis_winner(arr)
        

if __name__ == '__main__':
    main()
