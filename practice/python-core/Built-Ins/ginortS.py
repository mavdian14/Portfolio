# Enter your code here. Read input from STDIN. Print output to STDOUT
s = input()
#we create empty lists for all possible char types in s, move each char into its respective type list, then print the joined sorted lists in the order given by criteria
upper, lower, odd, even = [], [], [], []
for char in s:
    if char.isnumeric():
        if int(char)%2 == 0:
            even.append(char)
        else:
            odd.append(char)
    else:
        if char.isupper():
            upper.append(char)
        else:
            lower.append(char)

print(''.join(sorted(lower))+''.join(sorted(upper))+''.join(sorted(odd))+''.join(sorted(even)))
