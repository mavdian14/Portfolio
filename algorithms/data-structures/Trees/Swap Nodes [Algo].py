#!/bin/python3

import math
import os
import random
import re
import sys
from collections import deque
sys.setrecursionlimit(10000)

#
# Complete the 'swapNodes' function below.
#
# The function is expected to return a 2D_INTEGER_ARRAY.
# The function accepts following parameters:
#  1. 2D_INTEGER_ARRAY indexes
#  2. INTEGER_ARRAY queries
#

#create node class
class Node:
    #constructor
    def __init__(self,val):
        self.info = val
        self.left = None
        self.right = None
        
def swapNodes(indexes, queries):
    
    def create(root,indexes):
        q = deque([root])
        #traverse the indexes
        for x,y in indexes:
            temp = q.popleft()
            #left child
            if x != -1:
                temp.left = Node(x)
                q.append(temp.left)
            #right child
            if y!= -1:
                temp.right = Node(y)
                q.append(temp.right)
        return root
    
    def swap(root,k,level,l):
        if root:
            if level % k == 0:
                #swap the nodes
                root.left,root.right = root.right, root.left
            
            #in-order traversal
            swap(root.left,k,level+1,l)
            l.append(root.info)
            swap(root.right,k,level+1,l)
            
    # Create root node
    root = Node(1)
    #create the tree from indexes
    root = create(root,indexes)
    result = []
    #process the queries
    for k in queries:
        l = []
        swap(root,k,1,l)
        result.append(l)
    
    return result

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    indexes = []

    for _ in range(n):
        indexes.append(list(map(int, input().rstrip().split())))

    queries_count = int(input().strip())

    queries = []

    for _ in range(queries_count):
        queries_item = int(input().strip())
        queries.append(queries_item)

    result = swapNodes(indexes, queries)

    fptr.write('\n'.join([' '.join(map(str, x)) for x in result]))
    fptr.write('\n')

    fptr.close()
 
