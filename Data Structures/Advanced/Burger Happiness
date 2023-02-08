#!/bin/python3

import math
import os
import random
import re
import sys

from math import ceil, log
import sys

class SegmentTree(object):
    def __init__(self, seq=None, size=0):
        size = len(seq) if seq else size
        depth = int(ceil(log(size, 2)))
        if seq:
            lowest_lvl = 2 ** depth
            tree = [0] * (lowest_lvl - 1) + seq + [0] * (lowest_lvl - size)
            for d in range(depth - 1, -1, -1):
                for i in range(2 ** d - 1, 2 ** (d + 1) - 1):
                    tree[i] = max(tree[2 * i + 1], tree[2 * i + 2])
        else:
            tree = [0] * (2 ** (depth + 1) - 1)
        self.__tree = tree
        self.__pending = [0] * (2 ** depth - 1)

    def __str__(self):
        return str(self.__tree) + ',' + str(self.__pending)

    def query_point(self, index):
        index += len(self.__tree) // 2
        res = self.__tree[index]
        while index:
            index = (index - 1) // 2
            res += self.__pending[index]
        return res

    def query_left(self, index):
        index += len(self.__tree) // 2
        # Find first node that is not a right child
        while index and index % 2 == 0:
            index = (index - 1) // 2
        res = self.__tree[index]
        # Add pending updates to the result, if node is right child check
        # left as well
        while index:
            if index % 2 == 0:
                res = max(res, self.__tree[index - 1])
            index = (index - 1) // 2
            res += self.__pending[index]
        return res

    def query_right(self, index):
        index += len(self.__tree) // 2
        # Find first node that is not a left child
        while index % 2:
            index = (index - 1) // 2
        res = self.__tree[index]
        # Add pending updates to the result, if node is left child check
        # left as well
        while index:
            if index % 2:
                res = max(res, self.__tree[index + 1])
            index = (index - 1) // 2
            res += self.__pending[index]
        return res

    def update_point(self, index, diff):
        index += len(self.__tree) // 2
        val = self.__tree[index] + diff
        self.__tree[index] = val
        while index:
            index = (index - 1) // 2
            val += self.__pending[index]
            if val <= self.__tree[index]:
                break
            self.__tree[index] = val

    def update_left(self, index, diff):
        index += len(self.__tree) // 2
        # Handle sequence of right children and first left child
        if index and index % 2 == 0:
            while index and index % 2 == 0:
                index = (index - 1) // 2
            self.__pending[index] += diff
            self.__tree[index] += diff
        else:
            self.__tree[index] += diff
        # Here index points to either root or left child and
        # current node is updated
        # Update tree values all the way to the top
        while index:
            # If this is a right child then update the left child
            if index % 2 == 0:
                self.__pending[index - 1] += diff
                self.__tree[index - 1] += diff
            # Moved up the tree
            index = (index - 1) // 2
            # Update this node
            val = max(self.__tree[index * 2 + 1], self.__tree[index * 2 + 2])
            val += self.__pending[index]
            self.__tree[index] = val

    def update_right(self, index, diff):
        index += len(self.__tree) // 2
        # Handle sequence of left children and first right child
        if index % 2:
            while index % 2:
                index = (index - 1) // 2
            self.__pending[index] += diff
            self.__tree[index] += diff
        else:
            self.__tree[index] += diff
        # Here index points to either root or right child and
        # current node is updated
        # Update tree values all the way to the top
        while index:
            # If this is a left child then update the right child
            if index % 2:
                self.__pending[index + 1] += diff
                self.__tree[index + 1] += diff
            # Moved up the tree
            index = (index - 1) // 2
            # Update this node
            val = max(self.__tree[index * 2 + 1], self.__tree[index * 2 + 2])
            val += self.__pending[index]
            self.__tree[index] = val

n = int(sys.stdin.readline())
restaurants = []
for _ in range(n):
    restaurants.append(list(map(int, sys.stdin.readline().split())))
coords = {x: i for i, x in enumerate(sorted(map(lambda x: x[0], restaurants)))}
ascending = SegmentTree(size = n)
descending = SegmentTree(size = n)
res = 0
for x, a, b in restaurants:
    pos = coords[x]
    val = a
    if pos > 0:
        l = ascending.query_left(pos - 1)
        cur = ascending.query_point(pos)
        val = max(val, a + l - cur)
    if pos < n - 1:
        r = descending.query_right(pos + 1)
        cur = descending.query_point(pos)
        val = max(val, a + r - cur)
    res = max(res, val)
    ascending.update_point(pos, val)
    descending.update_point(pos, val)
    if b:
        ascending.update_left(pos, -b)
        descending.update_right(pos, -b)
print(res)
