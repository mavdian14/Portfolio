# Enter your code here. Read input from STDIN. Print output to STDOUT
from itertools import combinations

s,n = input().split()
for i in range(1,int(n)+1):
    #combinations(iterable, r) --> combinations object. Return successive r-length combinations of elements in the iterable. combinations(range(4), 3) --> (0,1,2), (0,1,3), (0,2,3), (1,2,3)
    for j in combinations(sorted(s),i):
        print(''.join(j))
    
