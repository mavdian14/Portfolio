def go():
    I=lambda:map(int,input().split())
    N=100002
    d=[0]*N
    P=[0]*N
    def add(p,c):
        d[c]=d[p]+1
        v=[p]
        for i in range(17):
            if not P[p] or len(P[p])<=i:break
            p=P[p][i];v.append(p)
        P[c]=v
    c=[[]for i in range(N)]
    for i in range(next(I())):
        x,y=I()
        if y: c[y].append(x)
        else: R=x
    l=[R]
    while l:
        p=l.pop()
        l.extend(c[p])
        for h in c[p]:
            add(p,h)
    del c,l
    for i in range(next(I())):
        l=list(I())
        if l[0]>1:
            _,x,k=l
            if d[x]<k:print(0);continue
            for i in range(17):
                if (1<<i)&k:x=P[x][i]
            print(x)
        elif l[0]:d[l[1]]=0
        else:add(l[1],l[2])

for t in range(int(input())):
    go()
        
