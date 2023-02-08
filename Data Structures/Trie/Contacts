#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'contacts' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts 2D_STRING_ARRAY queries as parameter.
#

def contacts(queries):
    mpp, res = {}, []
    
    for cmd,word in queries:
        if cmd == 'add':
            for i in range(len(word)):
                mpp[word[:i+1]] = mpp.get(word[:i+1],0)+1
        
        #for find cmd
        else:
            ans = 0
            ans += mpp.get(word,0)
            res.append(ans)
        
    return res
                
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    queries_rows = int(input().strip())

    queries = []

    for _ in range(queries_rows):
        queries.append(input().rstrip().split())

    result = contacts(queries)

    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
