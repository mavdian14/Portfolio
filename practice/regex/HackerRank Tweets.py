# Enter your code here. Read input from STDIN. Print output to STDOUT
import re
import string
import sys

n = int(input())
res = 0
for i in range(n):
    # Scan through string looking for a match to the pattern, returning a Match object, or None if no match was found.
    if(re.search(r'[hH][aA][cC][kK][eE][Rr][Rr][aA][nN][kK]',input())):
        res +=1

print(res)
    
