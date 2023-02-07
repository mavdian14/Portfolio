# Enter your code here. Read input from STDIN. Print output to STDOUT

import re

regex = re.compile(r"^(\d+)(?:[ -])(\d+)(?:[ -])(\d+)$")

for _ in range(int(input())):
    print("CountryCode={},LocalAreaCode={},Number={}".format(*regex.match(input()).groups()))
