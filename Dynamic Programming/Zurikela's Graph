Q = int(input().strip())
neighbors = {}
weights = []

def flood_fill(x, vis):
    vis.add(x)
    for y in neighbors[x]:
        if not y in vis:
            flood_fill(y, vis)
    return vis
    
def compute_indep(graph, curr, n):
    if n == len(graph):
        return sum(map(lambda x: weights[x], curr))
    elif weights[graph[n]] == 0:
        return compute_indep(graph, curr, n + 1) 
    ans = compute_indep(graph, curr, n + 1)  
    x = graph[n]
    possible = True
    for y in curr:
        if y in neighbors[x]:
            possible = False
            break
    if possible:
        ans = max(ans, compute_indep(graph, curr + [x], n + 1))
    return ans

for i in range(Q):
    query = input().strip()
    if query[0] == 'A':
        weights.append(int(query[1:]))
        neighbors[len(weights) - 1] = set()
    elif query[0] == 'B':
        x, y = map(int, query[1:].split())
        neighbors[x-1].add(y-1)
        neighbors[y-1].add(x-1)
    else: # 'C'
        component = list(flood_fill(int(query[1:]) - 1, set()))
        weights.append(compute_indep(component, [], 0))
        neighbors[len(weights) - 1] = set()
        for x in component:
            weights[x] = 0
            neighbors[x] = set()           
counted = set()
ans = 0
for i in range(len(weights)):
    if weights[i] > 0 and i not in counted:
        component = list(flood_fill(i, set()))
        for x in component:
            counted.add(x)
        ans += compute_indep(component, [], 0)
print(ans)
