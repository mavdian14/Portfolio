""" Node is defined as
class node:
  def __init__(self, data):
      self.data = data
      self.left = None
      self.right = None
"""
def check_binary_search_tree_(root):
    #create helper function
    def check(root,min_value,max_value):
        #base case
        if root is None:
            return True
        
        #general case
        if root.data < min_value or root.data > max_value:
            return False
        
        #traverse remaining nodes
        return check(root.left,min_value,root.data-1) and check(root.right,root.data+1.,max_value)
    
    return check(root,0,10000)
