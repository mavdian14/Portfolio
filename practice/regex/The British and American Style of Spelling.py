# Enter your code here. Read input from STDIN. Print output to STDOUT
import re
n = int(input())
texts = " ".join(input() for _ in range(n))

for _ in range(int(input())):
    amer = input()
    #re.sub() function returns a string by replacing the leftmost occurence (here ze$) with the given replacement (here se). In our case familiarize -> familiarise
    eng = re.sub("ze$", "se", amer)
    print(len(re.findall(f"({amer}|{eng})", texts)))
    
