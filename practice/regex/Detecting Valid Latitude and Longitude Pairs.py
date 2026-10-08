# Enter your code here. Read input from STDIN. Print output to STDOUT

import re

regex = re.compile(r"^\([+-]?(90(\.0+)?|([1-8]\d|[1-9])(\.\d+)?), [+-]?(180(\.0+)?|(1[0-7]\d|[1-9]\d?)(\.\d+)?)\)$")


for _ in range(int(input())):
    print("Valid" if regex.match(input()) else "Invalid")
