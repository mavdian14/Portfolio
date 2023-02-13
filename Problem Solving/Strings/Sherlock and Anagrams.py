#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'sherlockAndAnagrams' function below.
#
# The function is expected to return an INTEGER.
# The function accepts STRING s as parameter.
#

def sherlockAndAnagrams(s):
    n = len(s)
    numberOfAnagramPairs = 0
    for i in range(1, n): # length of the sublist 
# Key value pair dictionary to keep track of unique subStrings 
# and the count of their instances
        subStringsWithCounts = {}
        for j in range(n - i + 1): # Number of sublists in this iteration
# Get slice of string
            subString = s[j: j + i]
# Sort the characters in the slice alphabetically to make them 
# instances of a unique collection of characters (This allows us to 
# hash it into the subStringsWithCounts {} dictionary)
            sortedSubList = sorted(list(subString))
# Convert the sortedSubList back into a string
            sortedSubString = "".join(sortedSubList)

# There hasn't been a match of the sortedSubString
            if sortedSubString not in subStringsWithCounts:
                subStringsWithCounts[sortedSubString] = 1
# There is a match, add to the number of instances of that sortedSubString
            else:
                subStringsWithCounts[sortedSubString] += 1
            
            numberOfAnagramPairs += subStringsWithCounts[sortedSubString] - 1
            
    return numberOfAnagramPairs
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    q = int(input().strip())

    for q_itr in range(q):
        s = input()

        result = sherlockAndAnagrams(s)

        fptr.write(str(result) + '\n')

    fptr.close()
