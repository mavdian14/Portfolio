# Enter your code here. Read input from STDIN. Print output to STDOUT
from collections import Counter
x = int(input())
sizes=list(map(int,input().split()))
n=int(int(input()))
#Counter is a dict subclass where lists are transformed into dictionaries -> values are stored as keys, & occurences of that value in a list are stored as counter
sizes=Counter(sizes)
pr=0
for i in range(n):
    sz,pz=map(int,input().split())
    if(sizes[sz]):
        sizes[sz]-=1
        pr+=pz
        
print(pr)
