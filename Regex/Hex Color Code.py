# Enter your code here. Read input from STDIN. Print output to STDOUT
import re
pattern = r"(?<!^)(#(?:[a-f0-9]{6}|[a-f0-9]{3}))"
for _ in range(int(input())):
    me=re.findall(pattern, input(), flags=re.I)
    if len(me) > 0:
        print("\n".join(me))
