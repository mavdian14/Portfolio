# Enter your code here. Read input from STDIN. Print output to STDOUT
from itertools import permutations
s,n=input().split()
n=int(n)
#permutations(iterable[, r]) --> permutations object. Return successive r-length permutations of elements in the iterable.
#permutations(range(3), 2) --> (0,1), (0,2), (1,0), (1,2), (2,0), (2,1)
vals=list(permutations(s,n))
res=[]
for x in vals:
    res.append(''.join(x))
print('\n'.join(sorted(res)))
