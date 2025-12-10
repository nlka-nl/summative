ans = 0

for _ in range(int(input())):
    a = int(input())
    if a % 3 == 0 and a % 10 == 4:
        ans += a

print(ans)