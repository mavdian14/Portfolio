import sys
import heapq

n = int(input())
a = list(map(int, input().split()))
freq = dict()
for i in a:
    if i not in freq:
        freq[i] = 0
    freq[i] += 1
if len(freq) < n:
    print("NO")
    sys.exit()
exp_freq = 1
depth = 1
while 2**(depth - 1) < n:
    depth += 1
prev = dict()
ans = [0] * (n + n - 1)
while exp_freq <= n:
    v = list()
    v1 = list()
    for key in prev:
        v1.append((key, prev[key]))
    for key in freq:
        if freq[key] == depth:
            v.append(key)
    if len(prev) == 0:
        ans[0] = v[0]
        prev[v[0]] = 0
        freq[v[0]] -= 1
        exp_freq *= 2
        depth -= 1
        continue
    v.sort()
    v1.sort()
    cur = exp_freq // 2 - 1
    pq = list()
    j = 0
    for i in v:
        if i in prev:
            ans[prev[i] * 2 + 1] = i
            prev[i] = prev[i] * 2 + 1
            freq[i] -= 1
        else:
            while j < len(v1):
                if v1[j][0] < i:
                    heapq.heappush(pq, v1[j][1])
                    j += 1
                else:
                    break
            if len(pq) == 0:
                print("NO")
                sys.exit()
            temp = heapq.heappop(pq)
            ans[temp * 2 + 2] = i
            prev[i] = temp * 2 + 2
            freq[i] -= 1
    exp_freq *= 2
    depth -= 1
print("YES")
for i in ans:
    print(i, end=" ")
