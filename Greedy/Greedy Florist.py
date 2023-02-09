#!/bin/python3

import math
import os
import random
import re
import sys

#greedy algorithm at each moment/step in time of the algorithm, selects the optimal choicem thus, making it faster than other algorithms

#the first greedy algo is Djikstra's which finds the shortest path from a node to every other node in the graph. It's rules are: 1. everytime we visit a new node, we will choose the node iwth the smallest known distance. 2. once we move to the node, we check each of its neighbouring nodes. calc distance btwn the neighbouring nodes to the root nodes by summing cost of edges that lead to the new node (in a weighted graph). 3. if distance to a node is < a known distance, update shortest distance

#2nd algo is Prim's algo (min spanning trees), with steps as follows: 1. create a new tree with a single vertex (chosen randomly), 2. of all edges not yet in the tree, find min weighted edge and transfer it to the new tree, 3. repeat step 2 until all vertices are in the tree.

#3rd algo is Kruskal's algo with steps: 1. create a forest, (set of trees) where each vertex in graph is a seperate tree, 2. created sorted set S containing edges in graph, 3. while S non-empty & F is not yet spanning: remove an edge w/ min weight from S, If removed edge connects 2 different trees then add it to F, combining 2 trees into a single tree



# Complete the getMinimumCost function below.
def getMinimumCost(k, c):
    cost = 0
    n = len(c)
    m = 1
    
    #sort c in descending order
    c.sort(reverse=True)
    
    for i in range(n):
        cost += c[i]*m
        if (i+1)%k == 0:
            m+=1
    
    return cost
            
    

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    nk = input().split()

    n = int(nk[0])

    k = int(nk[1])

    c = list(map(int, input().rstrip().split()))

    minimumCost = getMinimumCost(k, c)

    fptr.write(str(minimumCost) + '\n')

    fptr.close()
