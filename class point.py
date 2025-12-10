eps = 1e-9
class Vector:
    def __init__(self, x = 0.0, y = 0.0, inp = False):

        if inp:
            x, y = map(float, input().split())

        self.x = float(x)
        self.y = float(y)
    def vect(self, other):
        return self.x * other.x + self.y * other.y
    def scal(self, other):
        return self.x * other.y - self.y * other.x
    def minus(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def perp(self):
        return Vector(-self.y, self.x)

    def __str__(self):
        return f"Vector({self.x}, {self.y})"
class Ray:
    def __init__(self, x = None, y = None, inp = False):

        if inp:
            self.x = Vector(inp = True)
            self.y = Vector(inp = True)
        else:
            self.x = x if x is not None else Vector(0, 0)
            self.y = y if y is not None else Vector(1, 0)
class Segment:
    def __init__(self, x = None, y = None, inp = False):

        if inp:
            self.x = Vector(inp = True)
            self.y = Vector(inp = True)
        else:
            self.x = x if x is not None else Vector(0, 0)
            self.y = y if y is not None else Vector(1, 0)
def crossRS(r: Ray, S: Segment):
    p = r.x
    a = S.x
    d = r.y.minus(r.x)
    e = S.y.minus(S.x)

    d2 = d.vect(d)

    if d2 < eps:
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

    tA = a.minus(p).vect(d) / d2
    tB = S.y.minus(p).vect(d) / d2
    tmax = max(tA, tB)

    if tmax < -eps:
        return None

    return a

r = Ray(inp = True)
s = Segment(inp = True)
inter = crossRS(r, s)

print(inter if inter is not None else None)