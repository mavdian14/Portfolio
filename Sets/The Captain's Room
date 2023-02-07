# Enter your code here. Read input from STDIN. Print output to STDOUT

# k = the number of people in a group
k = int(input())

# rooms is a tuple for each room number in the spaced out line
rooms = (int(x) for x in input().split(' '))
seen = {}

#populate the dictionary with room number: people in that room
for i in rooms:
    if not i in seen:
        seen[i] = 1
    else:
        seen[i] +=1

for key,val in seen.items():
    if val != k:
        print(key)
