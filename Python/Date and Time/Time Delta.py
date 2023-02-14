#!/bin/python3

import math
import os
import random
import re
import sys
from datetime import datetime as dt

# Complete the time_delta function below.
def time_delta(t1, t2):
    #Sun 10 May 2015 13:54:36 -0700
    #.strptime() creates a datetime object from the given string
    first = dt.strptime(t1,"%a  %d %b  %Y   %H:%M:%S %z")
    second = dt.strptime(t2,"%a  %d %b  %Y   %H:%M:%S %z")
    # .total_seconds() is used to return the total number of seconds covered for the specified duration of time instance
    return str(abs(int((first-second).total_seconds())))
    
    #%a  %d %B  %Y   %H %M %S  %z
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input())

    for t_itr in range(t):
        t1 = input()

        t2 = input()

        delta = time_delta(t1, t2)

        fptr.write(delta + '\n')

    fptr.close()
