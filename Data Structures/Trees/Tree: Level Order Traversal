

"""
Node is defined as
self.left (the left child of the node)
self.right (the right child of the node)
self.info (the value of the node)
"""
from collections import deque

def levelOrder(root):
    # a deque is a double ended queue which has a faster time complexity then a for loop on a list when dealing with boundary elements
    q = deque([root])
    
    #main logic
    while len(q):
        root = q.popleft()
        print(root, end=" ")
        
        #explore the next level
        if root.left:
            q.append(root.left)
        if root.right:
            q.append(root.right)
