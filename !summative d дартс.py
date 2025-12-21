import cv2
import numpy as np
import math

COLORS = {
    'team1': (0, 255, 0),
    'team2': (255, 0, 0),
    'text': (255, 255, 255)
}


class detect_dartboard:

    def __init__(self):

        self.center = (320, 240)
        self.radius = 215
        self.ring_width = 30


        self.angle = {
            20: 0, 1: 18, 18: 36, 4: 54, 13: 72, 6: 90,
            10: 108, 15: 126, 2: 144, 17: 162, 3: 180,
            19: 198, 7: 216, 16: 234, 8: 252, 11: 270,
            14: 288, 9: 306, 12: 324, 5: 342
        }


        self.zone_points = {
            0: 50,  # яблочко
            1: 25,  # кольцо вокруг центра
            2: 1,  # внутренняя область, х1
            3: 3,  # утроение, х3
            4: 1,  # средняя область, х1
            5: 2,  # удвоение, х2
            6: 0  # промах
        }

        self.team1_score = 0
        self.team2_score = 0
        self.current_team = 1
        self.drotiki = 0
        self.pframe = None

        self.darts = []

    def detect_b(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        # Поиск кругов (мишени)
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, 1, 100,
            param1 = 100, param2 = 30, minRadius = 100, maxRadius = 250
        )

        if circles is not None:
            circles = np.uint16(np.around(circles))

            mx = None

            for i in circles:
                if i[2] > mx[2]:
                    mx = i

            if mx is not None:
                self.center = (mx[0], mx[1])
                self.radius = mx[2]

                return True

        return False

    def detect_darts(self, frame):

        if self.pframe is None:
            self.pframe = frame
            return []

        cur = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        prev = cv2.cvtColor(self.pframe, cv2.COLOR_BGR2GRAY)

        dif = cv2.absdiff(cur, prev)

        _, thresh = cv2.threshold(dif, 60, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        d = []

        for i in contours:

            s = cv2.contourArea(i)

            if 20 < s < 100:
                m = cv2.moments(i)

                if int(m["m00"]) != 0:#площадь больше нуля
                    x = int(m["m10"] / m["m00"]) - self.center[0]
                    y = int(m["m01"] / m["m00"]) - self.center[1]

                    dist = math.sqrt(x * x + y * y)

                    if dist <= self.radius * 1.2:




detect_dartboard()

        