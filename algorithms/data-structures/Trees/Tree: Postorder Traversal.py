

"""
Node is defined as
self.left (the left child of the node)
self.right (the right child of the node)
self.info (the value of the node)
"""
def postOrder(root):
    #this is solved with recursion
    if root != None:
        #traverse to the left of root
        postOrder(root.left)
        #traverse to the right of root
        postOrder(root.right)
        print(root, end=" ")

