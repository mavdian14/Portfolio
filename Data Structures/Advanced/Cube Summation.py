#!/bin/python3

import math
import os
import random
import re
import sys

T = int(input())
for i in range(T):
    N,M = [int(s) for s in input().split()]
    data = {}
    for j in range(M):
        info = input().split()
        if info[0] == "UPDATE":
            data[info[1]+" "+info[2]+" "+info[3]] = int(info[4])
        else:
            x1 = int(info[1])
            y1 = int(info[2])
            z1 = int(info[3])
            x2 = int(info[4])
            y2 = int(info[5])
            z2 = int(info[6])
            res = 0
            for k,v in data.items():
                corr = [int(s) for s in k.split()]
                if corr[0] <= x2 and x1 <= corr[0] and corr[1] <= y2 and y1 <= corr[1] and corr[2] <= z2 and z1 <= corr[2]:
                    res += v
            print(res)
