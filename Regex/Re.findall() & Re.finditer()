# Enter your code here. Read input from STDIN. Print output to STDOUT
import re
#used to find 2+ consecutive vowels
sol=re.findall(r"(?<=[^aieuoAIEUO])[aiueoAIUEO]{2,}(?=[^aiueoAIUEO ])",input())

if sol:
    for s in sol:
        print(s)
else:
    print(-1)
