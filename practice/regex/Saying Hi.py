# Enter your code here. Read input from STDIN. Print output to STDOUT

import re

pattern = re.compile(r'hi [^d].*', re.I)

for _ in range(int(input())):
    match = re.match(pattern, input())

    if match:
        print(match.group())
    
