from math import gcd

def parseInput(f):
    return [f(x) for x in input().split()]

n=int(input())
array=parseInput(int)
stack=[]
#float(-inf) represents negative infinity
answer=float('-inf')
for number in array:
    for i in range(len(stack)):
        stack[i][0]=gcd(abs(stack[i][0]),abs(number))
        stack[i][1]+=number
        if number > stack[i][2]:
            stack[i][1]-=number-stack[i][2]
            stack[i][2]=number

    stack.append([number,0,number])
    newStack=[]
    for i in range(len(stack)):
        if newStack and newStack[-1][0] == stack[i][0]:
            if newStack[-1][1] <= stack[i][1]:
                if newStack[-1][1]+newStack[-1][2] > stack[i][1]+stack[i][2]:
                    newStack.append(stack[i])
                    continue
                newStack[-1][1]=stack[i][1]
                newStack[-1][2]=stack[i][2]
        else:
            newStack.append(stack[i])
    stack = newStack[:]
    answer=max(answer,max(abs(stack[i][0])*stack[i][1] for i in range(len(stack))))
print(answer)
