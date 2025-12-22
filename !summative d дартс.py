import cv2
import numpy as np
import time

COLORS = {
    'team1': (0, 255, 0),
    'team2': (255, 0, 0),
    'text': (255, 255, 255)
}


class dartboard:

    def __init__(self):

        self.center = None
        self.radius = None
        self.last_hit = None
        self.lteam = None

        self.rbull = 22
        self.rbullo = 41
        self.rsinner = 260
        self.rtriple = 300
        self.rsouter = 430
        self.rdouble = 470

        self.angle = {
            20: 0, 1: 18, 18: 36, 4: 54, 13: 72, 6: 90,
            10: 108, 15: 126, 2: 144, 17: 162, 3: 180,
            19: 198, 7: 216, 16: 234, 8: 252, 11: 270,
            14: 288, 9: 306, 12: 324, 5: 342
        }

        self.zone_points = {
            0: 50,
            1: 25,
            2: 1,
            3: 3,
            4: 1,
            5: 2,
            6: 0
        }

        self.team1_score = 0
        self.team2_score = 0
        self.pframe = None

    def detect_red(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower1 = np.array([0, 120, 70])
        upper1 = np.array([10, 255, 255])

        lower2 = np.array([170, 120, 70])
        upper2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower1, upper1)
        mask2 = cv2.inRange(hsv, lower2, upper2)

        mask = mask1 | mask2

        k = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2

        b = None
        bdist = 1e9

        for c in contours:
            s = cv2.contourArea(c)

            if s < 200:
                continue

            (x, y), r = cv2.minEnclosingCircle(c)

            if r < 8 or r > 40:
                continue

            dist = np.hypot(x - cx, y - cy)

            if dist < bdist:
                bdist = dist
                b = (int(x), int(y), int(r))

        if b is not None:
            self.center = (b[0], b[1])
            self.radius = b[2]
            return True

        return False

    def detect_darts(self, frame):

        cur = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cur = cv2.GaussianBlur(cur, (1, 1), 0)

        if self.pframe is None:
            self.pframe = cur
            return None

        dif = cv2.absdiff(self.pframe, cur)
        _, thresh = cv2.threshold(dif, 40, 255, cv2.THRESH_BINARY)

        k = np.ones((5, 5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, k)

        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        self.pframe = cur

        for c in contours:
            if cv2.contourArea(c) < 200:
                continue

            x, y, w, h = cv2.boundingRect(c)
            cx = x + w // 2
            cy = y + h // 2
            return cx, cy

        return None

    def get_sector(self, x, y):
        dx = x - self.center[0]
        dy = self.center[1] - y

        angle = (np.degrees(np.arctan2(dy, dx)) + 360 - 8) % 360

        for p, start in self.angle.items():
            if start <= angle < start + 18:
                return p

        return None

    def get_zone(self, x, y):
        dist = np.linalg.norm([x - self.center[0], y - self.center[1]])

        if dist < self.rbull:
            return 0
        elif dist < self.rbullo:
            return 1
        elif dist < self.rsinner:
            return 2
        elif dist < self.rtriple:
            return 3
        elif dist < self.rsouter:
            return 4
        elif dist < self.rdouble:
            return 5
        else:
            return 6

    def detect_team(self, frame, x, y, r=8):
        h, w, _ = frame.shape

        x1 = max(0, x - r)
        y1 = max(0, y - r)
        x2 = min(w, x + r)
        y2 = min(h, y + r)

        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            return None

        b, g, r = np.mean(roi, axis=(0, 1))

        return 1 if g > r else 2

    def register_score(self, frame, x, y):

        if self.last_hit is not None:
            if abs(self.last_hit[0] - x) <= 10 or abs(self.last_hit[1] - y) <= 10:
                return

        sector = self.get_sector(x, y)
        zone = self.get_zone(x, y)

        if sector is None or zone == 6:
            return

        team = self.detect_team(frame, x, y)

        if team is None:
            return

        points = sector * self.zone_points[zone]

        if team == 1:
            self.team1_score += points
        else:
            self.team2_score += points

        self.last_hit = (x, y)

        print(f"team = {team}, sector = {sector}, zone = {zone}, +{points}")


# ================== ЗАПУСК ВИДЕО ==================

cap = cv2.VideoCapture(r"C:\Users\user\PycharmProjects\pythonProject7\IMG_6576.MOV")
board = dartboard()
cen = False

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break

    cen = dartboard.detect_red(board, frame)

    dart = board.detect_darts(frame)

    cv2.circle(frame, board.center, board.radius, (255, 0, 0), 1)
    cv2.circle(frame, board.center, board.radius + board.rbullo, (0, 255, 255), 2)
    cv2.circle(frame, board.center,board.radius + board.rsinner, (255, 0, 0), 1)
    cv2.circle(frame, board.center, board.radius + board.rtriple, (0, 0, 255), 1)
    cv2.circle(frame, board.center, board.radius + board.rsouter, (0, 0, 255), 1)
    cv2.circle(frame, board.center, board.radius + board.rdouble, (0, 0, 255), 1)

    if dart:
        x, y = dart
        board.register_score(frame, x, y)
        cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)

    cv2.putText(frame, f"T1: {board.team1_score}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['team1'], 2)
    cv2.putText(frame, f"T2: {board.team2_score}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['team2'], 2)


    small = cv2.resize(frame, None, fx = 0.5, fy = 0.5)
    cv2.imshow("Dartboard", small)
    if cv2.waitKey(10) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()