#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'highestValuePalindrome' function below.
#
# The function is expected to return a STRING.
# The function accepts following parameters:
#  1. STRING s
#  2. INTEGER n
#  3. INTEGER k
#

def highestValuePalindrome(s, n, k):
    s = list(s)
    mark = [0]*n
    
    #change digits to palindrome
    l = 0 #left index
    r = n-1 # right index
    
    while l <= r:
        if s[l] != s[r]:
            if s[l] > s[r]:
                s[r] = s[l]
                mark[r] = 1
            else:
                s[l] = s[r]
                mark[l] =1
            k -=1
            
        l+=1
        r-=1
    
    #case: used too many changes
    if k < 0:
        return "-1"
    
    #maximize the digits
    l=0
    r=n-1
    #corner case to max mid digit
    while l <= r:
        if l == r and k>=1:
            s[l] = '9'
            break
    
        if s[l] < "9":
            #case: no changes before
            if mark[l] == 0 and mark[r] == 0 and k>= 2:
                s[l] = s[r] = '9'
                k-=2
                
            #case: changed before
            if (mark[l] == 1 or mark[r] == 1) and k >= 1:
                s[l] = s[r] = '9'
                k -=1
        l+=1
        r-=1    
    return "".join(s)
                
        
    

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    k = int(first_multiple_input[1])

    s = input()

    result = highestValuePalindrome(s, n, k)

    fptr.write(result + '\n')

    fptr.close()
