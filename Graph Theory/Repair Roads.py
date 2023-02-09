#!/bin/python3

import math
import os
import random
import re
import sys

import collections
import queue


def solve():
    n = int(input().strip())

    # read graph
    graph = dict((i, []) for i in range(0, n))

    for j in range(n - 1):
        x, y = [int(p) for p in input().strip().split()]
        graph[x].append(y)
        graph[y].append(x)

    # transform graph into tree
    level = 1

    root = 0
    q = queue.Queue()
    q.put((root, level, None))
    seen = set([])

    levels = collections.defaultdict(set)
    tree = {}

    while not q.empty():
        item, level, parent = q.get()
        levels[level].add(item)
        seen.add(item)

        tree[item] = dict(id=item, parent=parent, level=level, children=set([]),
                          leaf=None)

        for child in graph[item]:
            if child not in seen:
                #put an item into queue
                q.put((child, level + 1, item))
                seen.add(child)
                tree[item]['children'].add(child)

    # print('Levels: %s' % levels)
    # print('Tree: %s' % tree)

    # count clusters
    clusters = 1
    has_items_in_cluster = False

    for level in sorted(levels.keys(), reverse=True):
        for item in levels[level]:
            tree_item = tree[item]
            if not tree_item['children']:  # leaf
                tree_item['leaf'] = True
            else:
                has_items_in_cluster = True

                branches = 0
                for child in tree_item['children']:
                    if not tree[child]['leaf']:
                        branches += 1

                # branches == 0 -> visit point and go up
                # branches == 1 -> visit downstream, point and go up
                # branches % 2 == 0 -> have (branches // 2) clusters
                # branches % 2 == 1 -> have  (branches // 2) clusters and go up
                if branches >= 2:
                    new_clusters = branches // 2

                    clusters += new_clusters
                    # print('New clusters: %d' % new_clusters)

                    if branches % 2 == 0:
                        has_items_in_cluster = False
                        # cluster will also include road up
                        parent = tree_item['parent']
                        if parent is not None:
                            # print('Cut %s and %s' % (item, parent))
                            tree[parent]['children'].remove(item)

            # print(tree[item])

    # print('Tree: %s' % tree)

    if not has_items_in_cluster:
        clusters -= 1  # last cluster was created but has no items

    print(clusters)


t = int(input().strip())

for tt in range(t):
    solve()
