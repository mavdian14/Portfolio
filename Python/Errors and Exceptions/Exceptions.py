# Enter your code here. Read input from STDIN. Print output to STDOUT
lines = int(input())
for _ in range(lines):
    a, b =input().split()
    try:
        print(int(a)//int(b))
    except (ZeroDivisionError,ValueError) as e:
        print("Error Code:",e);
    
    #try exectutes the command below unless the except conditions are met
