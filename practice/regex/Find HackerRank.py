# Enter your code here. Read input from STDIN. Print output to STDOUT
import re

regexes = {re.compile(r"^hackerrank$"):0, re.compile(r"^hackerrank.+$"):1, re.compile(r"^.+hackerrank$"): 2, re.compile(r"^.+hackerrank.+$"):-1}

for _ in range(int(input())):
    text = input()
    #regexes.items() gives the ith key & jth value for dictionary
    print(*[j for i,j in regexes.items() if i.match(text)])
