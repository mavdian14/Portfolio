n = int(input())
s = set(map(int, input().split()))
for i in range(int(input())):
    c = input()
    if c == "pop":
        s.pop()
    else:
        command, value = c.split()
        if command == "discard":
            s.discard(int(value))
        else:
            s.remove(int(value))        
print(sum(s))
