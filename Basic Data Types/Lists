if __name__ == '__main__':
    N = int(input())
    #create a list of all possible commands from the input
    command=[]
    for i in range(N):
        command.append(input().split())
    
    result = []
    for i in range(N):
        if command[i][0]=='insert':
            #Insert object before index
            result.insert(int(command[i][1]), int(command[i][2]))
        elif command[i][0]=='print':
            print(result)
        elif command[i][0]=='remove':
            result.remove(int(command[i][1]))
        elif command[i][0]=='append':
            result.append(int(command[i][1]))
        elif command[i][0]=='sort':
            result.sort()
        elif command[i][0]=='pop':
            result.pop()
        elif command[i][0]=='reverse':
            result.reverse()
    
    
    
