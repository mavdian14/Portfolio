# Enter your code here. Read input from STDIN. Print output to STDOUT

# _ = the original # of elements in set A
_ = input()
# a is the set A
a = set(int(x) for x in input().split(' '))

#n is the number of other sets
n = int(input())
for _ in range(n):
    #op, _ = the operation with corresponding element
    op, _ = input().split(' ')
    # b is whichever set B for which operation is applied to set A given set B
    b = set(int(x) for x in input().split(' '))
    if op == "update":
        # |= bitwise OR operator
        a |= b
    elif op == "intersection_update":
        #bitwise AND operator &=
        a &= b
    elif op == "difference_update":
        a -= b
    elif op == "symmetric_difference_update":
        #XOR operator is symmetric_difference operator between 2 sets
        a ^= b

print(sum(a))
