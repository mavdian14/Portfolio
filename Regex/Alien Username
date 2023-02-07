# Enter your code here. Read input from STDIN. Print output to STDOUT
import re
n=int(input())
lines=[]
for i in range(0,n):
    #Extend list by appending elements from the iterable.
    lines.extend(input().split("\n"))

for l in lines:
    if(re.match("^[_.][0-9]{1,}[a-zA-Z]*[_]?$",l)!=None):
       print("VALID")
    else:
        print("INVALID")
