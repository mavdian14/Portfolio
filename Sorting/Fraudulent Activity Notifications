#!/bin/python3

import math
import os
import random
import re
import sys
#example: {2:1, 3:2, 4:1, 6:1}
# index = 3
#s = 1 => 3
# Complete the 'activityNotifications' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER_ARRAY expenditure
#  2. INTEGER d
#

def activityNotifications(expenditure, d):
    dic ={}
    
    def get_median(idx):
        s =0
        for i in range(201):
            freq = 0
            if i in dic:
                freq = dic[i]
            s += freq
            
            if s >= idx:
                return i
     
        
    result = 0
    
    for i in range(n): #n is defined below
        val = expenditure[i]
        
        #checking if expenditure on day i > min trailing days
        if i >= d:
            med = get_median(d//2 + d%2)
            
            if d%2 == 0:
                if val >= med + get_median(d//2 +1):
                    result+=1
                    
            else:
                if val >= med*2:
                    result +=1
        #add current val into dict sliding window                
        if val not in dic:
            dic[val] = 1
        else:
            dic[val] +=1
        
        #remove element out of sliding window
        if i >= d:
            prev = expenditure[i-d]
            dic[prev] -=1
    
    return result
            
                
            
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    d = int(first_multiple_input[1])

    expenditure = list(map(int, input().rstrip().split()))

    result = activityNotifications(expenditure, d)

    fptr.write(str(result) + '\n')

    fptr.close()
