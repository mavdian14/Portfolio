#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'maxSubarray' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts INTEGER_ARRAY arr as parameter.
#

def maxSubarray(arr):
    # Write your code here
    max_sum = 0
    curr_sum = 0
    # checking if all the arr values are negative
    neg_check = True
    neg_check = all([False for i in arr if i > 0])
    # if neg return the max of neg values
    if neg_check:
        return max(arr), max(arr)
    # else find the max value for subarray using Kadane's algo
    for i in arr:
        curr_sum += i
        # for each subarray sum compare it with max sum
        max_sum = max(curr_sum, max_sum)
        # if curr_sum becomes neg, discard that subarray and start fresh
        if curr_sum < 0:
            curr_sum = 0
     # finding max in a subsequence - order of elements need not be conserved   
    sub_seq_sum = sum([i for i in arr if i > 0])
    return max_sum, sub_seq_sum

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        n = int(input().strip())

        arr = list(map(int, input().rstrip().split()))

        result = maxSubarray(arr)

        fptr.write(' '.join(map(str, result)))
        fptr.write('\n')

    fptr.close()
