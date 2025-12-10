eps = 1e-9
class Vector:
    def __init__(self, x = 0, y = 0, inp = False):

        if inp:
            x, y  = map(float, input().split())

        self.x = x
        self.y = y

    def vect(self, other):
        return self.x * other.x + self.y * other.y

    def scal(self, other):
        return self.x * other.y - self.y * other.x

    def minus(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def perp(self):
        return Vector(-self.y, self.x)

    def __str__(self):
        return f"Vector({self.x}, {self.y})"# точность

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
            self.x = Vector(inp=True)
            self.y = Vector(inp=True)

        else:
            self.x = x if x is not None else Vector(0, 0)
            self.y = y if y is not None else Vector(1, 0)

def crossRS(r: Ray, S: Segment):
    p = r.x
    a = S.x

    s1 = r.y.minus(r.x)
    s2 = S.y.minus(S.x)
    d = r.y.minus(r.x)
    e = S.y.minus(S.x)
    e2 = e.vect(e)
    d2 = d.vect(d)

    if e2 < eps:
        if d2 < eps:
            ap = a.minus(p)

            if ap.vect(ap) < eps:
                return p

            return 1

        else:
            nd = d.perp()

            if abs(a.minus(p).vect(nd)) > eps:
                return 2

            t = a.minus(p).vect(d) / d2

            if t >= -eps:
                return a

            return 3

    nd = e.perp()
    if abs(d.vect(nd)) > eps:
        t = a.minus(p).vect(nd) / d.vect(nd)

        if t < -eps:
            return 4

        else:
            x = Vector(p.x + t * d.x, p.y + t * d.y)
            u = x.minus(S.x).vect(e) / e2

            if -eps <= u <= 1 + eps:
                return x

            return 5

    if d2 < eps:
        mnx = min(S.x.x, S.y.x) - eps
        mny = min(S.x.y, S.y.y) - eps
        mxx = max(S.x.x, S.y.x) - eps
        mxy = max(S.x.y, S.y.y) - eps

        if mnx <= p.x <= mxx and mny <= p.y <= mxy:
            return p

        return 6

    nd = d.perp()

    if abs(a.minus(p).vect(nd)) > eps:
        return 7

    t0 = S.x.minus(p).vect(d) / d2
    t1 = S.y.minus(p).vect(d) / d2
    a = []

    if t0 >= -eps:
        a.append(t0)

    if t1 >= eps:
        a.append(t1)

    if not a:
        return 8

    tmn = min(a)

    return Vector(p.x + tmn * d.x, p.y + tmn * d.y)

r = Ray(inp=True)
s = Segment(inp=True)
print(crossRS(r,s))

        




