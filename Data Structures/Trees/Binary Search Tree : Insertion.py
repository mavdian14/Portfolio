

#Node is defined as
#self.left (the left child of the node)
#self.right (the right child of the node)
#self.info (the value of the node)

    def insert(self, val):
        #going down the tree, if the value to be inserted is greater than the root, go down the right. If its less, go down the left. Use this logic for each node as you go down the tree
        newnode = Node(val)
        #case 1: root is NULL
        if self.root is None:
            self.root = newnode
            return self
        
        cur = self.root
        #traverse the nodes using while loop
        while cur:
            #case 2: value is lesser than root
            if val < cur.info:
                if cur.left is None:
                    cur.left = newnode
                    return self
                cur = cur.left
            #case 3: value is greater than root
            else:
                if cur.right is None:
                    cur.right = newnode
                    return self
                cur = cur.right
                    
            

