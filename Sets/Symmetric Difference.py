# Enter your code here. Read input from STDIN. Print output to STDOUT
num1=int(input())
listA=set(map(int, input().split(' ')))
num2=int(input())
listB=set(map(int, input().split(' ')))

setA = set(listA)
setB = set(listB)

tmp_set1 = setA.difference(setB)
tmp_set2 = setB.difference(setA)
result = tmp_set1.union(tmp_set2)
result = sorted(result)

for el in result:
    print(el)
