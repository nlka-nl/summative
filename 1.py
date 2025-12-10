import math

eps = 1e-9

class Vector:
    def __init__(self, x = 0.0, y = 0.0, inp=False):                                           # радиус-вектор r = {x, y}; ввод либо из аргументов, либо со stdin
        if inp:                                                                                # режим ввода со стандартного потока
            x, y = map(float, input().split())                                                 # читаем координаты точки (радиус-вектора)
        self.x = float(x)                                                                      # сохраняем x
        self.y = float(y)                                                                      # сохраняем y

    def vect(self, other):                                                                     # скалярное произведение (r, q) — используется для проекций
        return self.x * other.x + self.y * other.y                                             # (x1,y1)·(x2,y2)

    def scal(self, other):                                                                     # 2D-псевдоскаляр (аналог ориентированного «cross») — тест параллельности/коллинеарности
        return self.x * other.y - self.y * other.x

    def minus(self, other):                                                                    # разность радиус-векторов: r - r0
        return Vector(self.x - other.x, self.y - other.y)                                      # даёт направляющий вектор p (см. параметризацию)

    def perp(self):                                                                            # вектор, перпендикулярный данному (нормаль к направлению)
        return Vector(-self.y, self.x)                                                         # поворот на +90°

    def ugol(self, u):
        a = math.radians(u)
        pt = Vector(self.x + math.cos(a), self.y + math.sin(a))
        return Ray(self, pt)

    def koef(self):
        self.a = self.y - y
        self.b = x1 - x2
        self.c = -1 * (self.a * x1 + self.b * y1)

    def ispointonline():
        def __init__(self, p, a, b, c):
            if abs(p.x * a + p.y * b + c) < eps:
                self.ans = "YES"
            else:
                self.ans = "NO"

        def __str__(self):
            return f"{self.ans}"

    def __str__(self):                                                                         # требуемый формат печати результата
        return f"Vector({self.x}, {self.y})"                                                   # «Vector(x, y)» — как в условии

class Ray:
    def __init__(self, x = None, y = None, inp = False):                                       # луч f(O,R): задаётся двумя радиус-векторами O (начало) и R (точка на луче)
        if inp:                                                                                # ввод из stdin
            self.x = Vector(inp = True)                                                        # O
            self.y = Vector(inp = True)                                                        # R
        else:                                                                                  # значения по умолчанию
            if x is not None:
                self.x = x
            else:
                self.x = Vector(0, 0)

            if y is not None:
                self.y = y
            else:
                self.y = Vector(1, 0)

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
    p = r.x                                                                                    # p = r0 для луча (опорная точка в параметризации)
    a = S.x                                                                                    # a = опорная точка отрезка
    d = r.y.minus(r.x)                                                                         # d = направляющий вектор луча (m,n) в r = r0 + t d   (t∈[0,+∞))  :contentReference[oaicite:1]{index=1}
    e = S.y.minus(S.x)                                                                         # e = направляющий вектор отрезка (AB) в a + u e       (u∈[0,1])   :contentReference[oaicite:2]{index=2}

    d2 = d.vect(d)
    # |d|^2 — понадобится для проекций (t = ((X-p),d)/|d|^2)

    if d2 < eps:                                                                               # вырожденный «луч»: направления нет ⇒ это просто точка p
        mnx = min(S.x.x, S.y.x) - eps                                                          # осевой прямоугольник отрезка по X (для принадлежности точки отрезку)
        mny = min(S.x.y, S.y.y) - eps                                                          # по Y
        mxx = max(S.x.x, S.y.x) + eps                                                          # по X
        mxy = max(S.x.y, S.y.y) + eps                                                          # по Y

        if mnx <= p.x <= mxx and mny <= p.y <= mxy:                                            # p принадлежит [A,B] ⇒ точка пересечения есть
            return p                                                                           # ближайшая точка — p
        return None                                                                            # иначе пересечения нет

    denom = d.scal(e)                                                                          # det(d,e): ≠0 — линии не параллельны (пересекаются единственно)
    if abs(denom) > eps:                                                                       # общий случай (единственная точка)
        ap = a.minus(p)                                                                        # вектор AP
        t = ap.scal(e) / denom                                                                 # из r0 + t d = a + u e получаем t и u (метод Крамера в 2D-форме)
        u = ap.scal(d) / denom                                                                 # параметр отрезка
        if t >= -eps and -eps <= u <= 1 + eps:                                                 # t∈[0,+∞), u∈[0,1] — полу-прямая и отрезок по теории параметров    :contentReference[oaicite:3]{index=3}
            return Vector(p.x + t * d.x, p.y + t * d.y)                                        # возвращаем точку пересечения
        return None                                                                            # параметры не попали в допустимые интервалы — пересечения нет

    if abs(a.minus(p).scal(d)) > eps:                                                          # det(a-p,d)≠0 ⇒ параллельны и не коллинеарны (разные прямые)
        return None                                                                            # пересечения нет

    # Коллинеарность: луч и отрезок лежат на одной прямой (общее уравнение/каноническое эквивалентны).                           :contentReference[oaicite:4]{index=4}
    tA = a.minus(p).vect(d) / d2                                                               # параметр t точки A на луче: (A-p, d)/|d|^2  (проекция на d)
    tB = S.y.minus(p).vect(d) / d2                                                             # параметр t точки B
    tmax = max(tA, tB)
    # самая «дальняя» из концов по параметру t
    if tmax < -eps:                                                                            # оба конца «за спиной» луча (t<0) ⇒ не «освещается»
        return None                                                                            # пересечения нет (для луча)
    return a                                                                                   # по условию серии задач: при коллинеарности ответ — точка A (если «достижима»)

o = Vector(inp = True) #ray
n = int(input())
l = []
lp = [o]

for _ in range(n):
    v1 = Vector(inp = True)
    v2 = Vector(inp = True)
    l.append(Segment(v1, v2))
    lp.extend([v1, v2])

k = int(input())
s = 360 / k
res = []

for i in range(k):
    u = i * s
    r = o.rayangle(u)
    ans = None
    anst = float("inf")
    d = r.y.minus(r.x)
    d2 = d.vect(d)

    for j in l:
        a = crossRS(r, j)

        if a is None:
            continue
        else:
            t = Vector(a.x - o.x, a.y - o.y).vect(d) / d2

            if t >= -eps and t < anst:
                anst = t
                ans = a

    res.append(ans)

for i in res:
    print(f"{i.x:.7f} {i.y:.7f}")


import pygame                                                                             # подключаем pygame

minx1 = min(i.x for s in l for i in (s.x, s.y))
maxx1 = max(i.x for s in l for i in (s.x, s.y))
miny1 = min(i.y for s in l for i in (s.x, s.y))
maxy1 = max(i.y for s in l for i in (s.x, s.y))

lp.extend([i for i in res if i is not None])                                    # добавляем пересечения в рамку
minx = min(i.x for i in lp); maxx = max(i.x for i in lp)                      # X-диапазон
miny = min(i.y for i in lp); maxy = max(i.y for i in lp)                      # Y-диапазон
pad = 20.0                                                                                # поля
minx -= pad; maxx += pad; miny -= pad; maxy += pad                                        # расширяем
W, H = 900, 700                                                                           # размер кадра
pygame.init()                                                                             # старт
surf = pygame.Surface((W, H))                                                             # холст без окна
surf.fill((250, 250, 250))    # фон
rl = pygame.Surface((W, H), pygame.SRCALPHA)
sl = pygame.Surface((W, H), pygame.SRCALPHA)
ml = pygame.Surface((W, H), pygame.SRCALPHA)

def on_frame(v):
    l = abs(v.x - minx1) <= eps and (miny1 - eps) <= v.y <= (maxy1 + eps)
    r = abs(v.x - maxx1) <= eps and (miny1 - eps) <= v.y <= (maxy1 + eps)
    d = abs(v.y - miny1) <= eps and (minx1 - eps) <= v.x <= (maxx1 + eps)
    u = abs(v.y - maxy1) <= eps and (minx1 - eps) <= v.x <= (maxx1 + eps)

    return l or r or u or d
def to_screen(v):                                                                         # мировые → экранные
    sx = (v.x - minx) / (maxx - minx + 1e-12) * (W - 40) + 20                             # масштаб X
    sy = (1.0 - (v.y - miny) / (maxy - miny + 1e-12)) * (H - 40) + 20                     # инверсия Y
    return (int(round(sx)), int(round(sy)))                                               # пиксели

span = maxx - minx + maxy - miny
for i, v in enumerate(res):                                                           # рисуем лучи и точки
    if v is not None:
        pygame.draw.aaline(surf, (180, 180, 180, 200), to_screen(o), to_screen(v))
    else:
        ang = i * s                                                                        # угол
        dx = math.cos(math.radians(ang)); dy = math.sin(math.radians(ang))                    # направление
        far = Vector(o.x + dx * span, o.y + dy * span)                                  # —
        pygame.draw.aaline(surf, (180, 180, 180, 120), to_screen(o), to_screen(far))

for st in l:                                                                            # рисуем сегменты
    pygame.draw.line(surf, (40, 80, 220), to_screen(st.x), to_screen(st.y), 3)              # синий отрезок

for i in res:
    if i is not None and not on_frame(i):
        pygame.draw.circle(surf, (220, 80, 80), to_screen(i), 3)                          # точка пересечения
pygame.draw.circle(surf, (200, 40, 40), to_screen(o), 5)                                  # источник

surf.blit(rl, (0, 0))
surf.blit(sl, (0, 0))
surf.blit(ml, (0, 0))

pygame.image.save(surf, "rays_segments.png")                                              # сохраняем PNG
pygame.quit()                                                                             # завершение


