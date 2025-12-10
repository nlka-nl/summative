import math
import time

import pygame

class PygameFacade:
    def __init__(self, caption='Pokemons'):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()

    def draw_polygon(self, color, width=0, *args):
        pygame.draw.polygon(self.screen, color, args, width)

    def draw_rectangle(self, x, y, width, height, color, a=0):
        pygame.draw.rect(self.screen, color, pygame.Rect(x, y, width, height), a)

    def draw_line(self, x1, y1, x2, y2, color, width=1):
        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), width)

    def draw_circle(self, x, y, color, radius):
        pygame.draw.circle(self.screen, color, (x, y), radius)

    def draw_image(self, x, y, image):
        self.screen.blit(image, (x, y))

    def load_image(self, name):
        return pygame.image.load(name)

    def transform_scale(self, image, x, y):
        return pygame.transform.smoothscale(image, (x, y))

    def update_screen(self):
        pygame.display.flip()

    def clear_screen(self):
        self.screen.fill((0, 0, 0))

    def blit_text(self, txt, color, size, x, y):
        font = pygame.font.SysFont("Arial", size)
        text_surface = font.render(txt, True, color, None)
        self.screen.blit(text_surface, (x, y))

pygame_facade = PygameFacade()

class Point:
    def __init__(self, a=0, b=0, polar: bool = False):
        self.pol = polar
        if polar is True:
            self.x = a*math.cos(b)
            self.y = a*math.sin(b)
        else:
            if isinstance(a, Point):
                self.x = a.x
                self.y = a.y
            else:
                self.x = a
                self.y = b

    def __abs__(self) -> float:
        return math.hypot(self.x, self.y)

    def dist(self, a: int = 0, b: int = 0):
        if isinstance(a, Point):
            x = a.x
            y = a.y
        else:
            x = a
            y = b
        return math.hypot(self.x-x, self.y-y)

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

class Vector(Point):
    def __init__(self, a=0, b=0, c=0, d=0):
        if isinstance(a, Point) and isinstance(b, Point):
            i, j = b.x - a.x, b.y - a.y
        elif isinstance(a, Point):
            i, j = a.x, a.y
        else:
            i, j = c - a, d - b
        super().__init__(i, j)

    def dot_product(self, other):
        return self * other

    def cross_product(self, other):
        return self ^ other

    def __mul__(self, other):
        if isinstance(other, Point):
            return self.x * other.x + self.y * other.y
        if isinstance(other, int):
            return Point(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self * other

    def __xor__(self, other):
        return self.x * other.y - self.y * other.x

    def __str__(self):
        return f"Vector({self.x}, {self.y})"

    def find_degree(self, other):
        k = (other * self)/abs(other)/abs(self)
        k = math.degrees(math.acos(k))
        if self ^ other < 1e-8:
            k = 360-k
        return k

    @staticmethod
    def find_point(A, B, C, A1, B1, C1):
        if B != 0 and B1 != 0:
            x = (B1 * C - B * C1) / (B * A1 - A * B1)
            y = (-1 * A * x - C) / B
        elif B == 0 or B1 != 0:
            x = -C / A
            y = (-1 * A1 * x - C1) / B1
        elif B != 0 or B1 == 0:
            A, B, C, A1, B1, C1 = A1, B1, C1, A, B, C
            x = -C / A
            y = (-1 * A1 * x - C1) / B1
        return x, y

class Ray:
    def __init__(self, a =None, b =None, inp: bool = False):
        if inp:
            x1, y1 = map(int, input().split())
            x2, y2 = map(int, input().split())
            a = Point(x1, y1)
            b = Point(x2, y2)
        if isinstance(a, Point) and isinstance(b, float):
            x1, y1 = a.x, a.y
            EPS = 1e-5
            if 0 < b < 90:
                x1 += 100
                y1 -= abs(100 * math.tan(math.radians(b)))
            elif 180 > b > 90:
                x1 -= 100
                y1 -= abs(100 * math.tan(math.radians(b)))
            elif 180 < b < 270:
                x1 -= 100
                y1 += abs(100 * math.tan(math.radians(b)))
            elif 270 < b < 360:
                x1 += 100
                y1 += abs(100 * math.tan(math.radians(b)))
            elif abs(b - 0.0) < EPS:
                x1 += 100
            elif abs(b - 180.0) < EPS:
                x1 -= 100
            elif abs(b - 90.0) < EPS:
                y1 -= 100
            elif abs(b - 270.0) < EPS:
                y1 += 100
            b = Point(x1, y1)

        self.a = b.y - a.y
        self.b = a.x - b.x
        self.c = -self.a * b.x - self.b * b.y
        self.start_x = a.x
        self.start_y = a.y
        self.point_x = b.x
        self.point_y = b.y

    def check_point(self, p: Point):
        a, b, c, d, e, f = p.x, p.y, self.start_x, self.start_y, self.point_x, self.point_y
        V1 = Vector(e - c, f - d)
        V2 = Vector(a - c, b - d)
        EPS = 1e-5
        if abs(V1) * abs(V2) - V1 * V2 < EPS:
            return True
        else:
            return False

class Segment:
    def __init__(self, a = None, b = None, inp: bool = False):
        if inp:
            x1, y1 = map(int, input().split())
            x2, y2 = map(int, input().split())
            a = Vector(x1, y1)
            b = Vector(x2, y2)
        self.start_x, self.start_y = (a.x, a.y)
        self.end_x, self.end_y = (b.x, b.y)
        self.a = b.y - a.y
        self.b = a.x - b.x
        self.c = -self.a * b.x - self.b * b.y

    def is_point_on_segment(self, point):
        EPS = 1e-8
        v1 = Vector(self.end_x - self.start_x, self.end_y - self.start_y)
        v2 = Vector(point.x - self.start_x, point.y - self.start_y)
        k = v1 ^ v2
        if abs(k) > EPS:
            return False
        d1 = v1 * v2
        d2 = v1 * v1
        if -EPS <= d1 <= d2 + EPS:
            return True
        else:
            return False

def crossRS(r: Ray, s:Segment):
    EPS = 1e-8
    A, B, C, A1, B1, C1 = r.a, r.b, r.c, s.a, s.b, s.c
    if abs(A * B1 - A1 * B) < EPS:  # параллельны
        if (A * C1 - A1 * C == 0) or (B * C1 - B1 * C == 0):  # параллельны и совпадают
            if r.check_point(Point(s.start_x, s.start_y)) == True or r.check_point(Point(s.end_x, s.end_y)):  # отрезок и луч имеют общие точки
                v1 = Vector(s.start_x, s.start_y, r.start_x, r.start_y)
                v2 = Vector(s.end_x, s.end_y, r.start_x, r.start_y)
                if s.start_y > r.start_y > s.end_y or s.start_y < r.start_y < s.end_y:
                    x, y = r.start_x, r.start_y
                elif s.start_x > r.start_x > s.end_x or s.start_x < r.start_x < s.end_x:
                    x, y = r.start_x, r.start_y
                elif abs(v1) < abs(v2):
                    x, y = s.start_x, s.start_y
                else:
                    x, y = s.end_x, s.end_y
            else:  # отрезок и луч не имеют общие точки
                return None
        else:  # параллельны и не совпадают
            return None

    else:  # поиск общей точки если не параллельны
        x1, y1 = Vector.find_point(A, B, C, A1, B1, C1)
        if s.is_point_on_segment(Point(x1, y1)) and r.check_point(Point(x1, y1)):  # если точка на луче и на отрезке
            x, y = x1, y1
        else:  # точка пересечения не попала на луч или отрезок
            return None

    return (x, y)

def f(r: Ray):  # точка пересечения луча и фигур
    ans_x = 1e8
    ans_y = 1e8
    for i in a:
        ans = crossRS(r, i)
        if ans is not None:
            v1 = Vector(ans[0], ans[1], x, y)
            v2 = Vector(ans_x, ans_y, x, y)
            if abs(v1) < abs(v2):
                ans_x = ans[0]
                ans_y = ans[1]
    return ans_x, ans_y

with open('inf.txt', 'r') as file:
    x, y = map(float, file.readline().split())
    a = []  # координаты отрезков фигур
    s = []
    n = int(file.readline())
    for i in range(n):
        x1, y1 = map(float, file.readline().split())
        x2, y2 = map(float, file.readline().split())
        a.append(Segment(Point(x1, y1), Point(x2, y2)))
        s.append((x1, y1))
        s.append((x2, y2))

def update(x, y):  # обновление точек пересечения
    b = []
    c = []
    ans = []
    for i in range(len(s)):
        k = Vector(x, y, s[i][0], s[i][1]).find_degree(Vector(x, y, x + 100, y))
        r = Ray(Point(x, y), k)
        r1 = Ray(Point(x, y), (k + 0.1))
        r2 = Ray(Point(x, y), (k - 0.1))
        ans_x, ans_y = f(r2)
        ans.append((ans_x, ans_y, k-0.1))
        ans_x, ans_y = f(r1)
        ans.append((ans_x, ans_y, k+0.1))
        ans_x, ans_y = f(r)
        b.append(Segment(Point(x, y), Point(ans_x, ans_y)))
        ans.append((ans_x, ans_y, k))

    ans.sort(key=lambda x: x[2], reverse=True)
    segments = []
    EPS = 1e-8
    for i in range(0, len(ans)):
        if (abs(ans[i][0]-ans[i-1][0]) > EPS or abs(ans[i][1]-ans[i-1][1]) > EPS) and (x, y) != (ans[i][0], ans[i][1]):
            segments.append(Segment(Point(x, y), Point(ans[i][0], ans[i][1])))
    return segments

x, y = 489, 485
segments = update(x, y)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if pygame.mouse.get_pressed()[0] is True:
            x, y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
            segments = update(x, y)
    pygame_facade.clear_screen()
    for i in range(0, len(segments)):
        pygame_facade.draw_polygon((255, 241, 204), 0, (segments[i].start_x, segments[i].start_y),
                                   (segments[i].end_x, segments[i].end_y), (segments[i-1].end_x, segments[i-1].end_y))
        #pygame_facade.draw_line(segments[i].start_x, segments[i].start_y, segments[i].end_x, segments[i].end_y, (255, 0, 0), 3)

    for i in a:
        pygame_facade.draw_line(i.start_x, i.start_y, i.end_x, i.end_y, (255, 0, 0), 3)
    pygame_facade.draw_circle(x, y, (255, 0, 0), 5)
    pygame_facade.update_screen()
    pygame_facade.clock.tick(30)

