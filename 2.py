eps = 1e-9

class Vector:

    def __init__(self, x = 0.0, y = 0.0, inp = False):

        if inp:
            x, y = map(float, input().split())

        self.x = float(x)
        self.y = float(y)

    def dot(self, other):#скалярное произведение, если равно 0, то они перп
        return self.x * other.x + self.y * other.y

    def scal(self, other):#векторное произведение, если 0, то они коллинеарны
        return self.x * other.y - self.y * other.x

    def minus(self, other):#разность двух векторов
        return Vector(self.x - other.x, self.y - other.y)

    def perp(self):#поворот на 90 против часовой
        return Vector(-self.y, self.x)


class Ray:

    def __init__(self, x = None, y = None, inp = False):

        if inp:
            self.x = Vector(inp = True) #начальная точка
            self.y = Vector(inp = True) #направляющий вектор
        else:
            if x is not None:
                self.x = x
            else:
                self.x = Vector(0, 0)

            if y is not None:
                self.y = y
            else:
                self.y = Vector(1, 0)

    def form(self, x1, y1, x2, y2):
        a = y2 - y1
        b = x1 - x2
        c = -1 * (a * x1 + b * y1)

        return a, b, c

    def __str__(self):
        return f"Vector({self.x}, {self.y})"

class Segment:

    def __init__(self, x = None, y = None, inp = False):

        if inp:
            self.x = Vector(inp = True)
            self.y = Vector(inp = True)
        else:
            if x is not None:
                self.x = x
            else:
                self.x = Vector(0, 0)

            if y is not None:
                self.y = y
            else:
                self.y = Vector(1, 0)

def crossRS(r: Ray, S: Segment):
    p = r.x
    a = S.x
    d = r.y.minus(r.x)
    e = S.y.minus(S.x)

    d2 = d.dot(d)

    if d2 < eps:# если луч это точка
        mnx = min(S.x.x, S.y.x) - eps
        mny = min(S.x.y, S.y.y) - eps
        mxx = max(S.x.x, S.y.x) + eps
        mxy = max(S.x.y, S.y.y) + eps

        if mnx <= p.x <= mxx and mny <= p.y <= mxy:
            return p
        return None

    denom = d.scal(e)

    if abs(denom) > eps:
        ap = a.minus(p)
        t = ap.scal(e) / denom
        u = ap.scal(d) / denom
        if t >= -eps and -eps <= u <= 1 + eps:
            return Vector(p.x + t * d.x, p.y + t * d.y)
        return None

    if abs(a.minus(p).scal(d)) > eps:
        return None

    tA = a.minus(p).dot(d) / d2
    tB = S.y.minus(p).dot(d) / d2
    tmax = max(tA, tB)

    if tmax < -eps:
        return None

    return a

r = Ray(inp = True)
s = Segment(inp = True)
print(crossRS(r, s))

