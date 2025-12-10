class Vector:
    def __init__(self, x=None, y=None, inp=False):
        if inp:
            x, y = map(float, input().split())
        self.x = x
        self.y = y

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, factor):
        return Vector(self.x * factor, self.y * factor)

    def __str__(self):
        return f"Vector({self.x}, {self.y})"

    def cross(self, other):
        return self.x * other.y - self.y * other.x

class Ray:
    def __init__(self, inp=False):
        self.p = Vector(inp=inp)
        self.q = Vector(inp=inp)

class Segment:
    def __init__(self, inp=False):
        self.a = Vector(inp=inp)
        self.b = Vector(inp=inp)

def crossRS(r: Ray, s: Segment):
    p, q = r.p, r.q
    a, b = s.a, s.b
    d1 = q - p
    d2 = b - a
    denom = d1.cross(d2)
    if abs(denom) < 1e-10:
        # Они коллинеарны
        # Пересечение если отрезок лежит на луче
        ap = a - p
        if abs(d1.cross(ap)) < 1e-10:
            # Отрезок лежит на луче
            t0 = (a - p).x * d1.x + (a - p).y * d1.y
            t1 = (b - p).x * d1.x + (b - p).y * d1.y
            if max(t0, t1) < 0:
                return None
            t = min(t0, t1)
            if t >= 0:
                pt = a if t0 < t1 else b
                return pt
            else:
                pt = a if t1 >= 0 else b
                return pt if (pt - p).x * d1.x + (pt - p).y * d1.y >= 0 else None
        else:
            return None
    else:
        ap = a - p
        t = ap.cross(d2) / denom
        u = ap.cross(d1) / denom
        if t >= -1e-8 and 0 <= u <= 1:
            intersect = p + d1 * t
            return Vector(round(intersect.x, 6), round(intersect.y, 6))
        else:
            return None
r = Ray(inp=True)
s = Segment(inp=True)
print(crossRS(r,s))