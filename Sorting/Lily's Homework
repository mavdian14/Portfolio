#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'lilysHomework' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER_ARRAY arr as parameter.
#

def lilysHomework(arr):
    #create function to find no. of swap
    def no_of_swaps(arr):
        indexmap = {}
        
        for i in range(len(arr)):
            indexmap[arr[i]] = i
            
        #sort the array
        sorted_arr = sorted(arr)
        result = 0
        
        for i in range(len(arr)):
            if arr[i] != sorted_arr[i]:
                result +=1
                
                #swap element index
                swap_index = indexmap[sorted_arr[i]]
                #update swapping index
                indexmap[arr[i]] = swap_index
                #swap operation
                arr[i], arr[swap_index] = arr[swap_index], arr[i]
                
        return result
    
    #[::] is a slicing operator, in this case only skipping over 1 element i.e. steps successively    
    normal_order = no_of_swaps(arr[::])
    reverse_order = no_of_swaps(arr[::-1])
    return min(normal_order,reverse_order)
    

    
    

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    n = int(input().strip())

    arr = list(map(int, input().rstrip().split()))

    result = lilysHomework(arr)

    fptr.write(str(result) + '\n')

    fptr.close()
