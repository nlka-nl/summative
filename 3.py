import math
eps = 1e9

class Point:

    def __init__(self, a = 0, b = 0):
        if isinstance(a, Point):
            self.x = a.x
            self.y = a.y
        else:
            self.x = a
            self.y = b

    def lenth(self) -> float: #длина вектора от (0,0)
        return math.hypot(self.x, self.y)

    def dist(self, a):
        return math.hypot(self.x - a.x, self.y - a.y)

class Vector(Point):

    def __init__(self, a = 0, b = 0, c = 0, d = 0):
        if isinstance(a, Point) and isinstance(b, Point):
           x, y = b.x - a.x, b.y - a.y

        elif isinstance(a, Point):
           x, y = a.x, a.y

        else:
           x, y = c - a, d - b

        super().__init__(x, y)

    def dot(self, other): #скалярное произведение, если равно 0, то они перп
        return self.x * other.x + self.y * other.y

    def scal(self, other): #векторное произведение, если 0, то они коллинеарны
        return self.x * other.y - self.y * other.x

    def minus(self, other): #разность двух векторов
        return Vector(self.x - other.x, self.y - other.y)

    def perp(self) :#поворот на 90 против часовой
        return Vector(-self.y, self.x)

    def angle(self, other):
        f = math.degrees(math.atan2(self.y, self.x))
        s = math.degrees(math.atan2(other.y, other.x))
        d = f - s

        if d < 0:
            d += 360

        return d

class Ray:
    def __init__(self, x = None, y = None, inp = False):
        if inp:
            x1, y1 = map(int, input().split())
            x2, y2 = map(int, input().split())

        else:
            x1, y1 = x.x, x.y
            x2, y2 = y.x, y.y

        self.a = y2 - y1
        self.b = x1 - x2
        self.c = -1 * (self.a * x1 + self.b * y1)

        self.sx = x.x
        self.sy = x.y #начальная точка
        self.px = y.x
        self.py = y.y #направляющая луч точка

    def check(self, p: Point):
        r = Vector(self.px - self.sx, self.py - self.sy)
        rp = Vector(p.x - self.sx, p.y - self.sy)

        if Vector.scal(r, rp) > eps:
            return False

        return Vector.dot(r, rp) >= -eps



start = Point(0, 0)
e = Point(1, 2)
ray = Ray(start, e)
p = Point(-10, -3)

if Ray.check(ray, p):
    print(1)
else:
    print(2)


