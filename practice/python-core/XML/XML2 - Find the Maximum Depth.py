

maxdepth = 0
def depth(elem, level):
    global maxdepth #program to modify a global variable inside the function
    if (level==maxdepth):
        maxdepth+=1
    for i in elem:
        depth(i,level+1)
    

