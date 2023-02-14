#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'abbreviation' function below.
#
# The function is expected to return a STRING.
# The function accepts following parameters:
#  1. STRING a
#  2. STRING b
#

def abbreviation(a, b):
    n = len(a)
    m = len(b)

    # init dp_list => O(n * m)
    dp_list = [[False] * (m + 1) for _ in range(n + 1)] # + 1 b/c including empty string
    dp_list[0][0] = True # abbreviation("", "") => True (base case)
    # establish init results for abbreviation(a, "") column
    for i, char_from_A in enumerate(a): # O(n)
        if char_from_A.islower():
            dp_list[i + 1][0] = True
        else:
            break

    # fill in dp_list # => O(n * m)
    for j in range(1, m + 1): # looping through B str first (order doesn't matter)
        char_from_B = b[j - 1] # - 1 b/c indeces b/t dp_list and string are off by 1
        for i in range(1, n + 1): # looping through A str second (order doesn't matter)
            char_from_A = a[i - 1]

            # Main logic
            if char_from_A.isupper():
                prev_result = dp_list[i-1][j-1]
                if prev_result:
                    dp_list[i][j] = char_from_A == char_from_B
            else: # char_from_A is lowercase
                above_result = dp_list[i-1][j]            
                if char_from_A.upper() == char_from_B: # characters match
                    prev_result = dp_list[i-1][j-1]
                    # result is either removing character or including as capital
                    dp_list[i][j] = above_result or prev_result
                else: # remove lowercase character
                    dp_list[i][j] = above_result

    # print('\n'.join([' '.join(["T" if val else "F" for val in row]) for row in dp_list]))
    return "YES" if dp_list[-1][-1] else "NO"
    
           
            

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    q = int(input().strip())

    for q_itr in range(q):
        a = input()

        b = input()

        result = abbreviation(a, b)

        fptr.write(result + '\n')

    fptr.close()
