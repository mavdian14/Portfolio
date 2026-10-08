# Enter your code here. Read input from STDIN. Print output to STDOUT
import re
from re import match, compile
#re is the regular expression package used to detect floating point #s

pattern = compile('^[-+]?[0-9]*\.[0-9]+$')
for _ in range(int(input())):
    print(bool(pattern.match(input())))
    
