#!/bin/python3

import math
import os
import random
import re
import sys

def maximizingFunction(a, queries):
    results = [0] * q
    sums = {}
    summary = 0
    temp = 1
    for i in range(len(a)):
        if a[i] == 1:
            temp = temp * (-1)
        summary += temp
        if i in all_x:
            sums[i] = [summary, temp]
        if i in queries:
            for x, index in queries[i]:
                length = i-x+1
                try:
                    temp_2 = (summary - sums[x-1][0])*sums[x-1][1] + 1
                except:
                    temp_2 = summary + 1
                a1 = (length+1+temp_2)//2
                results[index] = a1*(length+1-a1)
                if index == 3:
                    print(sums[x-1][1])

        



    for x, y, index in queriesk:
        length = y-x+1
        if length%2==1:
            results[index] = ((length+1)//2) ** 2
        else:
            results[index] = ((length//2)+1) * (length//2)
    return results

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    nq = input().split()

    n = int(nq[0])

    q = int(nq[1])

    a = list(map(int, input().rstrip().split()))


    queries = {}

    queries = {}
    queriesk = []
    all_x = set()
    for i in range(q):
        x, y, k, index = list(map(int, input().rstrip().split()))+ [i]
        if k > 0:
            queriesk.append([x, y, index])
        else:
            try:
                queries[y].append([x, index])
                all_x.add(x-1)
            except:
                queries[y] = [[x, index]]
                all_x.add(x-1)
    result = maximizingFunction(a, queries)
    #result = sorted(result, key=itemgetter(1))
    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
