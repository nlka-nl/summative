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

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def dist(self, x = None, y = None):
        if x is None and y is None:
            return abs(self)

        if isinstance(x, Point):
            return math.hypot(self.x - x.x, self.y - x.y)

        return math.hypot(self.x - x, self.y - y)

    def __str__(self):
        return f"({self.x}, {self.y})"

class Vector(Point):
    def __init__(self, *args):
        if len(args) == 2 and isinstance(args[0], Point):
            super().__init__(args[1].x - args[0].x, args[1].y - args[0].y)

        elif len(args) == 4:
            super().__init__(args[2] - args[0], args[3] - args[1])

        elif len(args) == 1:
            super().__init__(args[0].x, args[0].y)

        else:
            super().__init__(args[0], args[1])

    def dot_product(self, other):
        return self.x * other.x + self.y * other.y

    def __mul__(self, other):
        if isinstance(other, int):
            return Point(self.x * other, self.y * other)

        return self.x * other.x + self.y * other.y

    def __rmul__(self, other):
        return self * other

    def cross_product(self, other):
        return self ^ other

    def __xor__(self, other):
        return self.x * other.y - self.y * other.x

a, b, c, d, e, f = map(int, input().split())
p1 = Point(a, b)
p2 = Point(c, d)
p3 = Point(e, f)
v23 = Vector(p2, p3)
v12 = Vector(p1, p2)
eps = 10**(-10)

if v12.x 

if abs(v23 ^ v12) > eps and Vector.dot_product(v23, v12) < eps:
    print("YES")
else:
    print("NO")