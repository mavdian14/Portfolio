# Enter your code here. Read input from STDIN. Print output to STDOUT
import re
t = int(input())
for _ in range(t):
    try:
        re.compile(input())
        print(True)
    except re.error:
        print(False)
        
    #to check if regular expression, must use re.compile except when re.error is true
