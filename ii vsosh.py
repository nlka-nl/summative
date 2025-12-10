'''
a = []
n = int(input())
for _ in range(n):
    h, m = map(int, input().split(':'))
    a.append(h * 60 + m)

s = 24 * 60
ans = 0
for i in range(n - 1):
    ans += (a[i + 1] - a[i] + s) % s

print(ans - 1)

5
13:03
17:03
19:30
23:59
00:15
'''

