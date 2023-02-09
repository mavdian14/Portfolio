import collections


n,h,ii = map(int, input().split())
dp = [[0]*h for _ in range(n)]
for i in range(n):
    x = list(map(int, input().split()))
    for j in x[1:]: dp[i][j-1] += 1
last = collections.deque()
for j in range(h):
    x = last.popleft() if j >= ii else 0
    for i in range(n):
        dp[i][j] += max(0 if j == 0 else dp[i][j-1], x)
    last.append(max(k[j] for k in dp))
print(max(k[-1] for k in dp))
