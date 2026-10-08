# Enter your code here. Read input from STDIN. Print output to STDOUT
import re

n = int(input())
texts = " ".join(input() for _ in range(n))

for _ in range(int(input())):
    eng = input()
    amer = re.sub("our", "or", eng)
    print(len(re.findall(rf"\b({eng}|{amer})\b", texts)))
