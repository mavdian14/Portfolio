# Enter your code here. Read input from STDIN. Print output to STDOUT
import re
for _ in range(int(input())):
    S = input()
    t = re.search(r"^[456]\d{15}$|^[456]\d{3}-\d{4}-\d{4}-\d{4}$",S)
    if(t):
        if(re.search(r"(\d)\1{3,}|(\d)\2{1}-(\d)\2{1}|(\d)\4{4}-",S
        )):
            print("Invalid")
        else:
            print("Valid")
    else:
        print("Invalid")
            
        
        
