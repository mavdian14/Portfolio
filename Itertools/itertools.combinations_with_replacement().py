# Enter your code here. Read input from STDIN. Print output to STDOUT
from itertools import combinations_with_replacement
s,k= input().split(' ')
s=[x for x in s]
k=int(k)
s.sort()
#combinations_with_replacement(iterable, r) --> combinations_with_replacement object. Return successive r-length combinations of elements in the iterable allowing individual elements to have successive repeats. combinations_with_replacement('ABC', 2) --> AA AB AC BB BC CC
l=list(combinations_with_replacement(s,k))
l.sort()
for i in l:
    s = ''
    for k in i:
        s+=k
    print(s)
