n, queries = map(int, input().split())
# data structure to keep parent and size of each sub group
people = [{'parent': i, 'n': i, 'size': 1} for i in range(n)]

# return the index of the parent
def parent_index(n):
    while people[n]['parent'] != people[n]['n']:
    # path compression (works logically without this, but will
    # fail last 3 tests without it)
        people[n]['parent'] = people[people[n]['parent']]['parent']
        n = people[n]['parent']
    return n

for _ in range(queries):
    q = input().split()
    if q[0] == 'Q':
        n = int(q[1])-1
    # print the size of parent
        print(people[parent_index(n)]['size'])
    elif q[0] == 'M':
        p1, p2 = parent_index(int(q[1])-1), parent_index(int(q[2])-1)
        if p1 != p2:
    # set the parent of p2 to be the parent of p1
            people[p2]['parent'] = people[p1]['parent']
            people[p1]['size'] += people[p2]['size']
