# Enter your code here. Read input from STDIN. Print output to STDOUT
import re
l=[]
for _ in range(int(input())):
    pattern = r'<(\w+)'
    #Return a list of all non-overlapping matches in the string. If one or more capturing groups are present in the pattern, return a list of groups; this will be a list of tuples if the pattern has more than one group.
    match = re.findall(pattern,input())
    for i in match:
        l.append(i)        
a = sorted(set(l))
print(';'.join(a))
    
