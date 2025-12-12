import math
eps = 1e9

class Point:

    def __init__(self, x = 0, y = 0):

        if isinstance(x, Point):
            self.x = x.x
            self.y = y.y
        else:
            self.x = x
            self.y = y

    def __abs__(self) -> float: #длина вектора от (0,0)
        return math.hypot(self.x, self.y)

    def dist(self, a):
        return math.hypot(self.x - a.x, self.y - a.y)

class Vector(Point):

    def __init__(self, *args):
        if len(args) == 2 and isinstance(args[0], Point):
            super().__init__(args[1].x - args[0].x, args[1].y - args[0].y)

        elif len(args) == 4:
            super().__init__(args[2] - args[0], args[3] - args[1])

        else:
           super().__init__(args[0], args[1])

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
            self.start = Point(x1, y1)
            self.dirpoint = Point(x2, y2)

        else:
            self.start = x
            self.dirpoint = y

        self.a = self.dirpoint - self.start
        self.b = self.start - self.dirpoint
        self.c = -1 * (self.a * self.start.x + self.b * self.start.y)

    def dir_vector(self):#вектор направления луча
        return Vector(self.start, self.dirpoint)

    def check(self, point):
        '''проверяем лежит ли точка на прямой луча с помощью уравнения прямой'''

        ck = self.a * point.x + self.b * point.y + self.c

        if abs(ck) > eps:
            return False

        '''проверяем, что точка лежит в том направлении от начала луча'''

        vect_point = Vector(self.start, point)#вектор от начала луча к точке
        vect_dir = self.dir_vector()#направляющий вектор луча

        return vect_dir.dot(vect_point) >= -eps


start = Point(0, 0)
e = Point(1, 2)
ray = Ray(start, e)
p = Point(-10, -3)

if Ray.check(ray, p):
    print(1)
else:
    print(2)


