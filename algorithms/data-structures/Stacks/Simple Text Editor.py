# Enter your code here. Read input from STDIN. Print output to STDOUT
stack = []
string = ""

for _ in range(int(input())):
    #split each line into query type & action
    t = input().split()
    #check for query type:
    #query type1: append to string
    if t[0] == '1':
        stack.append(string)
        string += t[1]
    #type2:remove last k chars from string
    elif t[0] == '2':
        stack.append(string)
        string = string[:-int(t[1])]
    #type3: print the kth char of s
    elif t[0] == '3':
        print(string[int(t[1])-1])
    #type4: undo previous operation
    else:
        string = stack.pop()
        
