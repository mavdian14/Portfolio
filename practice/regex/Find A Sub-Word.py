# Enter your code here. Read input from STDIN. Print output to STDOUT

import re
n = int(input())
words = []
for i in range(0, n):
    #splits input line into all the sub-words following the criteria into elements in words
    words += re.split("[^a-zA-Z0-9_]+", input())
t = int(input())
for i in range(0, t):
    s = input()
    count = 0
    for w in words:
        if (re.match("[a-zA-Z0-9_]+"+s+"[a-zA-Z0-9_]+", w)): count += 1
    print(count)
