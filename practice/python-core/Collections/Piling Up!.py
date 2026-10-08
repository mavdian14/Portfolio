# Enter your code here. Read input from STDIN. Print output to STDOUT
ans = []
n = int(input())

#for loop for each test case, cube size c &
# sl sidelengths of each cube
for i in range(n):
    c = int(input())
    sl = list(map(int, input().split()))
    
    #if leftmost sidelength less than rightmost it, pop it
    for _ in range(c-1):
        if sl[0] >= sl[len(sl)-1]:
            a = sl[0]
            sl.pop(0)
        elif sl[0] < sl[len(sl)-1]:
            a = sl[len(sl)-1]
            sl.pop(len(sl)-1)
        else:
            pass
        if len(sl) == 1:
            ans.append("Yes")
            
        if((sl[0] > a) or (sl[len(sl)-1] > a)):
            ans.append("No")
            break
print("\n".join(ans))
