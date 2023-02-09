#!/bin/python3

import math
import os
import random
import re
import sys
from collections import defaultdict

from collections import defaultdict

def maximumPeople(towns, cloud_start, cloud_end):
    towns = sorted(towns)
    cloud_start = sorted(cloud_start)
    cloud_end = sorted(cloud_end)

    cloud_start_i = 0
    cloud_end_i = 0
    clouds = set()

    d = defaultdict(int)
    free = 0
    for town_i in range(len(towns)):
        town_x = towns[town_i][0]
        while cloud_start_i < len(cloud_start) and cloud_start[cloud_start_i][0] <= town_x:
            clouds.add(cloud_start[cloud_start_i][1])
            cloud_start_i += 1
        while cloud_end_i < len(cloud_end) and cloud_end[cloud_end_i][0] < town_x:
            clouds.remove(cloud_end[cloud_end_i][1])
            cloud_end_i += 1
        if len(clouds) == 1:
            towns[town_i][2] = list(clouds)[0]
            d[list(clouds)[0]] += towns[town_i][1]
        elif len(clouds) == 0:
            free += towns[town_i][1]

    return max(d.values(), default=0) + free


def main():
    n = int(input().strip())
    p = [int(x) for x in input().strip().split()]
    x = [int(x) for x in input().strip().split()]
    towns = [[xi, pi, -1] for xi, pi in zip(x, p)]
    m = int(input().strip())
    y = [int(x) for x in input().strip().split()]
    r = [int(x) for x in input().strip().split()]
    cloud_start = [[y[i]-r[i], i] for i in range(m)]
    cloud_end = [[y[i]+r[i], i] for i in range(m)]
    result = maximumPeople(towns, cloud_start, cloud_end)
    print(result)

if __name__ == "__main__":
    main()
