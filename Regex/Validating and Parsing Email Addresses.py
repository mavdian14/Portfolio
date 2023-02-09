# Enter your code here. Read input from STDIN. Print output to STDOUT
import re
# \w matches an alphanumeric 
pattern = r'<[a-z](\w|-|_|\.)+@[a-z]+\.[a-z]{1,3}>'
for _ in range(int(input())):
    match = input()
    if bool(re.search(pattern, match)):
        print(match)
    else:
        continue
