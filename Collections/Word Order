# Enter your code here. Read input from STDIN. Print output to STDOUT
from collections import OrderedDict

#create an ordered dictionary where each unique word is a key & the # of occurences of that word is the value
n = int(input())
d=OrderedDict()
for i in range(n):
    s=input()
    if s in d.keys():
        d[s] += 1
    else:
        d[s] = 1

print(len(d.keys()))
print(' '.join([str(d[k]) for k in d.keys()]))
