# Enter your code here. Read input from STDIN. Print output to STDOUT
n,x = map(int,input().split())
score = []
for _ in range(x):
    #for each line of grades, we will append a nested lists into score
    score.append(list(map(float,input().split())))
 #for each new list due to zip   
for stud in list(zip(*score)):
    print("%.1f"%(sum(stud)/len(stud)))
