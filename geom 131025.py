
'''
class Line:
    def __init__(self, x1, y1, x2, y2):
        self.a = y2 - y1
        self.b = x1 - x2
        self.c = -1 * (self.a * x1 + self.b * y1)


    def __str__(self):
        return f'{int(self.a)} {int(self.b)} {int(self.c)}'

x1, y1, x2, y2 = map(int, input().split())
l = Line(x1, y1, x2, y2)
print(l)

class Line:
    def __init__(self, x1, y1, x2, y2):
        self.a = x2
        self.b = y2
        self.c = -1 * (self.a * x1 + self.b * y1)

    def __str__(self):
        return f'{int(self.a)} {int(self.b)} {int(self.c)}'

x1, y1, x2, y2 = map(int, input().split())
l = Line(x1, y1, x2, y2)
print(l)
-16 21 -5


import math
class Point:
    def __init__(self, x,y = None, polar = False):

        if isinstance(x, Point):
            self.x = x.x
            self.y = x.y

        elif polar:
            self.x = x * math.cos(y)
            self.y = x * math.sin(y)
        else:
            self.x = x
            self.y = y

eps = 10**(-10)
class Line:
    def __init__(self, p, a, b, c):
        if abs(p.x * a + p.y * b + c) < eps:
            self.ans = "YES"
        else:
            self.ans = "NO"

    def __str__(self):
        return f"{self.ans}"

x1, y1, a, b, c = map(int, input().split())
p = Point(x1, y1)
l = Line(p, a, b, c)
print(l)


import math
class Line:
    def __init__(self, x1, y1, a, b, c):
        self.p = abs(a * x1 + b * y1 + c) / math.sqrt(a * a + b * b)

    def __str__(self):
        return f"{self.p}"

x1, y1, a, b, c = map(int, input().split())
l = Line(x1, y1, a, b, c)
print(l)

class Line:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def find(self, other):
        return f"{(self.b * other.c - other.b * self.c) / (self.a * other.b - other.a * self.b)} {(other.a * self.c - self.a * other.c) / (self.a * other.b - other.a * self.b)}"


a1, b1, c1, a2, b2, c2 = map(int, input().split())
l1 = Line(a1, b1, c1)
l2 = Line(a2, b2, c2)
print(Line.find(l1, l2))


class Line:
    def __init__(self, x1, y1, x2, y2):
        self.a = y2 - y1
        self.b = x1 - x2
        self.c = -1 * (self.a * x1 + self.b * y1)

    def peres(self, l1, l2):
        self.xans = (l1.b * l2.c - l2.b * l1.c) / (l1.a * l2.b - l2.a * l1.b)
        self.yans = (l2.a * l1.c - l1.a * l2.c) / (l1.a * l2.b - l2.a * l1.b)


    def __str__(self):
        return f'{int(self.a)} {int(self.b)} {int(self.c)}'

'''