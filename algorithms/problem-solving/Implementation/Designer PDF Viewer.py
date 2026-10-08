#!/bin/python3

import math
import os
import random
import re
import sys
import string

#
# Complete the 'designerPdfViewer' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER_ARRAY h
#  2. STRING word
#

def designerPdfViewer(h, word):
    w_len = len(word)
    #the alphabet array
    st = string.ascii_lowercase
    max_h = 0
    
    for ch in word:
        #assign i the index of that letter in the alphabet array
        i = st.index(ch)
        max_h = max(max_h,h[i])
    ans = max_h*w_len
    return ans
        

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    h = list(map(int, input().rstrip().split()))

    word = input()

    result = designerPdfViewer(h, word)

    fptr.write(str(result) + '\n')

    fptr.close()
