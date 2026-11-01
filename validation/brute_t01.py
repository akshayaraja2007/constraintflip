import sys
a = list(map(int, sys.stdin.read().split()))
n, k = a[0], a[1]
arr = a[2:2+n]
ans = 0
for i in range(n):
    s = 0
    for j in range(i, n):
        s += arr[j]
        if s == k:
            ans += 1
print(ans)
