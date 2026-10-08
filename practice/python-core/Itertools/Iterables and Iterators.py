# Enter your code here. Read input from STDIN. Print output to STDOUT
N = int(input())
D = input().split()
K = int(input())

from itertools import combinations

contain = 0
total = 0
for c in combinations(D, K):
    if "a" in c:
        contain += 1
    total += 1
print(contain/total)
