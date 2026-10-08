#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'timeInWords' function below.
#
# The function is expected to return a STRING.
# The function accepts following parameters:
#  1. INTEGER h
#  2. INTEGER m
#

def timeInWords(h, m):
    ho=d[h]
    if m not in[0,15,30,45]:
        mi=d[m] if m<30 else d[60-m]
    if m==0:
        return ho+' o\' clock'
    elif m==15:
        return 'quarter past '+ho
    elif m==30:
        return 'half past '+ho
    elif m<30:
        return mi+' minutes past '+ho if m>1 else 'one minute past '+ho
    elif m==45:
        return 'quarter to '+d[h+1]
    else:
        return mi+' minutes to '+d[h+1] if m<59 else 'one minute to '+ho
d={1:'one',2:'two',3:'three',4:'four',5:'five',
6:'six',7:'seven',8:'eight',9:'nine',10:'ten',
11:'eleven',12:'twelve',13:'thirteen',14:'fourteen',
16:'sixteen',17:'seventeen',18:'eighteen',19:'nineteen',
20:'twenty',21:'twenty one',22:'twenty two',23:'twenty three',
24:'twenty four',25:'twenty five',26:'twenty six',27:'twenty seven',
28:'twenty eight',29:'twenty nine'}

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    h = int(input().strip())

    m = int(input().strip())

    result = timeInWords(h, m)

    fptr.write(result + '\n')

    fptr.close()
