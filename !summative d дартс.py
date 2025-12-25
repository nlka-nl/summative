import cv2
import numpy as np
class dartboard:
    def __init__(self):

        self.center = None #центр мишени
        self.radius = None #радиус яблочка
        self.last_hit = None #координаты последнего удра

        self.rbull = 22 #настройка радиусов для видео
        self.rbullo = 41
        self.rsinner = 260
        self.rtriple = 300
        self.rsouter = 430
        self.rdouble = 470

        self.bull_coef = 1.0
        self.bullo_coef = 1.9
        self.sinner_coef = 12.0
        self.triple_coef = 13.8
        self.souter_coef = 19.5
        self.double_coef = 21.4


        # детектим что, дротик остановился
        self.stable_frames = 0  #стабильные кадры
        self.stable_point = None  #точка, куда попал дротик
        self.hits = []

        self.angle = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5] #порядок секторов по часовой
        self.pogr = 0 #смещение двадцатки по углу на видео

        self.team1_score = 0
        self.team2_score = 0
        self.pframe = None #предыдущий кадр для сравнения

    def is_new_hit(self, point, r = 15):

        for x, y in self.hits:
            if np.hypot(point[0] - x, point[1] - y) < r:
                return False

        return True

    def detect_red(self, frame):# нахождения яблочка с помощью накладывания красной маски
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

            if s < 200: #слишком маленькие не подходят
                continue

            (x, y), r = cv2.minEnclosingCircle(c)

            if r < 8 or r > 40:
                continue

            dist = np.hypot(x - cx, y - cy) #расстояние от центра

            if dist < bdist:
                bdist = dist
                b = (int(x), int(y), int(r))

        if b is not None:
            self.center = (b[0], b[1])
            self.radius = b[2]
            return True

        return False

    def detect_darts(self, frame): #определение брошен ли дротик

        if self.center is None or self.radius is None:
            return None

        cur = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cur = cv2.equalizeHist(cur)
        cur = cv2.GaussianBlur(cur, (5, 5), 0)

        if self.pframe is None:
            self.pframe = cur
            return None

        dif = cv2.absdiff(self.pframe, cur)
        _, thresh = cv2.threshold(dif, 12, 255, cv2.THRESH_BINARY)

        mask = np.zeros_like(thresh)
        cv2.circle(mask, self.center, int(self.radius * 21), 255, -1)
        thresh = cv2.bitwise_and(thresh, mask)

        k = np.ones((5, 5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, k)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, k)

        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        barea = 0
        best = None

        for c in contours:

            if cv2.contourArea(c) < 80:
                continue

            x, y, w, h = cv2.boundingRect(c)
            cx = x + w //2
            cy = y + h // 2

            if self.is_new_hit((cx, cy)):
                if cv2.contourArea(c) > barea:
                    barea = cv2.contourArea(c)
                    best = (cx, cy)

        self.pframe = cur

        if best is None:

            if self.stable_point is not None:
                self.stable_frames += 1

                if self.stable_frames >= 6: #чтобы он засчитывал дротик только после приземления, не во время броска
                    self.stable_frames = 0
                    hit = self.stable_point
                    self.stable_point = None

                    if self.is_new_hit(hit):
                        self.hits.append(hit)

                    return hit

            return None

        if self.stable_point is None:
            self.stable_point = best
            self.stable_frames = 1

            return None

        dist = np.hypot(best[0] - self.stable_point[0], best[1] - self.stable_point[1])

        if dist < 4:
            self.stable_frames += 1

        else:
            self.stable_point = best
            self.stable_frames = 1

        if self.stable_frames >= 6:
            hit = self.stable_point
            self.stable_point = None
            self.stable_frames = 0

            if self.is_new_hit(hit):
                self.hits.append(hit)

                return hit

        return None

    def calibrate(self, x, y):
        cx, cy = self.center
        dx = x - cx
        dy = cy - y

        deg = (np.degrees(np.arctan2(dy, dx)) + 360) % 360
        angle_real = (90 - deg) % 360
        self.pogr = (-angle_real) % 360

    def get_sector(self, x, y):
        dx = x - self.center[0]
        dy = self.center[1] - y

        deg = (np.degrees(np.arctan2(dy, dx)) + 360) % 360
        angle_real = (90 - deg) % 360
        angle_corrected = (angle_real + self.pogr) % 360
        index = int((angle_corrected + 9) // 18) % 20

        return self.angle[index]

    def get_zone(self, x, y):
        dist = np.hypot(x - self.center[0], y - self.center[1])

        if dist < self.rbull:
            return 'bull'

        if dist < self.rbullo:
            return 'outer_bull'

        if dist < self.rsinner:
            return 'single_inner'

        if dist < self.rtriple:
            return 'triple'

        if dist < self.rsouter:
            return 'single_outer'

        if dist < self.rdouble:
            return 'double'

        return 'miss'

    def detect_team(self, frame, x, y, r=10):
        h, w = frame.shape[:2]
        x1, y1 = max(0, x - r), max(0, y - r)
        x2, y2 = min(w, x + r), min(h, y + r)

        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            return None

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        h = hsv[:, :, 0]
        s = hsv[:, :, 1]

        mask = s > 60

        if np.count_nonzero(mask) < 10:
            return None

        h = h[mask]

        green = np.logical_and(h > 35, h < 85)

        red = np.logical_or(h < 10, h > 160)

        if np.mean(green) > 0.4:
            return 1

        if np.mean(red) > 0.4:
            return 2

        return None

    def register_score(self, frame, x, y):

        sector = self.get_sector(x, y)
        zone = self.get_zone(x, y)
        team = self.detect_team(frame, x, y)

        if zone == 'miss' or team is None:
            return

        m = 1

        if zone == 'triple':
            m = 3

        if zone == 'double':
            m = 2

        if zone == 'bull':
            m = 2

        if zone != 'bull' and zone != 'outer_bull':

            points = sector * m

        else:
            if zone == 'bull':
                points = 50

            else:
                points = 25

        if team == 1:
            self.team1_score += points
        elif team == 2:
            self.team2_score += points

        self.last_hit = (x, y)
        print(f"sector = {sector}, zone = {zone}, +{points}")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Камера не открылась")
    exit()
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)

for _ in range(20):
    cap.read()

def mouse(event, x, y, p, f):
    if event == cv2.EVENT_LBUTTONDOWN:
        ox = int(x / 0.5)
        oy = int(y / 0.5)

        if board.center is None:
            print("Center not detected yet; wait.")
            return

        board.calibrate(ox, oy)
        print("Clicked sector (should be 20")

cv2.namedWindow("Dartboard")
cv2.setMouseCallback("Dartboard", mouse)

board = dartboard()
cen = False

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break

    if board.detect_red(frame):
        pass

    dart = board.detect_darts(frame)

    if dart is not None:
        x, y = dart
        board.register_score(frame, x, y)
        cv2.circle(frame, (x, y), 9, (0, 0, 255), -1)

    cen = dartboard.detect_red(board, frame)

    if board.center:
        cx, cy = board.center
        r = board.radius

        cv2.circle(frame, (cx, cy), int(r * board.bull_coef), (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), int(r * board.bullo_coef), (0, 255, 255), 2)
        cv2.circle(frame, (cx, cy), int(r * board.sinner_coef), (255, 0, 0), 1)
        cv2.circle(frame, (cx, cy), int(r * board.triple_coef), (0, 0, 255), 2)
        cv2.circle(frame, (cx, cy), int(r * board.souter_coef), (255, 0, 0), 1)
        cv2.circle(frame, (cx, cy), int(r * board.double_coef), (0, 0, 255), 2)


    cv2.putText(frame, f"Team 1: {board.team1_score}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Team 2: {board.team2_score}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


    small = cv2.resize(frame, None, fx = 0.5, fy = 0.5)

    cv2.imshow("Dartboard", small)
    if cv2.waitKey(20) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()