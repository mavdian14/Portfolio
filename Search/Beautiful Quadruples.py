#!/bin/python3

import os
import sys

#
# Complete the beautifulQuadruples function below.
#
def beautifulQuadruples(a, b, c, d):
    # if a^b == c^d then its 0
    a,b,c,d = sorted([a,b,c,d])
    mem = [0]*(2*d)
    count = total = 0
    
    for i in range(1,c+1):
        for j in range(i,d+1):
            mem[i^j] += 1
            total +=1
    
    for i in range(1,b+1):
        for j in range(1, min(a,i)+1):
            count += total - mem[i^j]
        #to remove duplicates    
        for k in range(i,d+1):
            mem[i^k] -= 1
            total -=1
            
    return count
            
    
    

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    abcd = input().split()

    a = int(abcd[0])

    b = int(abcd[1])

    c = int(abcd[2])

    d = int(abcd[3])

    result = beautifulQuadruples(a, b, c, d)

    fptr.write(str(result) + '\n')

    fptr.close()
