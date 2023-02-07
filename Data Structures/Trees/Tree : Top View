

"""
Node is defined as
self.left (the left child of the node)
self.right (the right child of the node)
self.info (the value of the node)
"""
def topView(root):
    #create a dictionary to populate with each node, the level its on, & signify that with a key
    d = {}
    
    #create a function for traversing
    def traverse(root, key, level):
        if root:
            #key not present in dictionary
            if key not in d:
                d[key] = [root,level]
            # key with lesser level
            elif d[key][1] > level:
                d[key] = [root,level]
                
            #traverse to the left and right
            traverse(root.left,key-1,level+1)
            traverse(root.right,key+1,level+1)
    
    traverse(root,0,0)
    # print the elements in order
    for key in sorted(d):
        print(d[key][0], end=" ")
        
