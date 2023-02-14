# Enter your code here. Read input from STDIN. Print output to STDOUT
n = int(input())
lst=list(map(int,input().split()))
#print for all() with 2 conditions met:
#1. all integers are positive
#2. at least one integer is palindromic (any single digit is palindromic). for integers > 1 digit, 151 is palindromic 

#here [::-1] reverse the order of digits in an integer: a = 10, a[::-1] = 01
print(all([all(i>0 for i in lst) and any(i == int(str(i)[::-1]) for i in lst)]))
