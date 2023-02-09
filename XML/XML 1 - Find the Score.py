

def get_attr_number(node):
    #.iter() in XML creates a tree iterator over all elements/subelements in the document, returning all elements w/ a matching tag
    val = 0
    for child in node.iter():
        #print(child)
        #print(child.attrib)
        val+=len(child.attrib)
    
    return val
        
        

