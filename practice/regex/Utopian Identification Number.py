# Enter your code here. Read input from STDIN. Print output to STDOUT
import re

regex = re.compile(r"^[a-z]{,3}\d{2,8}[A-Z]{3,}$")
for _ in range(int(input())):
    print("VALID" if regex.match(input()) else "INVALID")
