import cv2
import numpy as np

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

        self.darts = []

    def detect_board(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        # Поиск кругов (мишени)
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, 1, 100,
            param1 = 100, param2 = 30, minRadius=100, maxRadius=250
        )

        