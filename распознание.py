'''
A

#создаем детектор
handsDetector = mp.solutions.hands.Hands(
    static_image_mode=True,
    max_num_hands=2,
    min_detection_confidence=0.85)

im = cv2.imread('input.jpg')
flipped = np.fliplr(im)

flippedRGB = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)
results = handsDetector.process(flippedRGB)

if results.multi_hand_landmarks is not None:
    print("YES")
else:
    print("NO")

handsDetector.close()
'''

import cv2
import mediapipe as mp
import numpy as np

handsDetector = mp.solutions.hands.Hands(
    static_image_mode=True,
    max_num_hands=2,
    min_detection_confidence=0.85)

im = cv2.imread('input.png')
flipped = np.fliplr(im)

flippedRGB = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)
results = handsDetector.process(flippedRGB)

if results.multi_hand_landmarks is not None:
    if "Left" in str(results.multi_handedness[0]):
        if results.multi_hand_landmarks[0].landmark[4].x > results.multi_hand_landmarks[0].landmark[20].x:
            if results.multi_hand_landmarks[0].landmark[4].x > results.multi_hand_landmarks[0].landmark[0].x and \
                    results.multi_hand_landmarks[0].landmark[4].y < results.multi_hand_landmarks[0].landmark[1].y and \
                    results.multi_hand_landmarks[0].landmark[8].y < results.multi_hand_landmarks[0].landmark[5].y and \
                    results.multi_hand_landmarks[0].landmark[12].y < results.multi_hand_landmarks[0].landmark[9].y and \
                    results.multi_hand_landmarks[0].landmark[16].y < results.multi_hand_landmarks[0].landmark[13].y and \
                    results.multi_hand_landmarks[0].landmark[20].y < results.multi_hand_landmarks[0].landmark[17].y:
                ans = 'paper'

    elif "Right" in str(results.multi_handedness[0]):
        if results.multi_hand_landmarks[0].landmark[4].x < results.multi_hand_landmarks[0].landmark[20].x:
            if results.multi_hand_landmarks[0].landmark[4].x < results.multi_hand_landmarks[0].landmark[0].x and \
                    results.multi_hand_landmarks[0].landmark[4].y < results.multi_hand_landmarks[0].landmark[1].y and \
                    results.multi_hand_landmarks[0].landmark[8].y < results.multi_hand_landmarks[0].landmark[5].y and \
                    results.multi_hand_landmarks[0].landmark[12].y < results.multi_hand_landmarks[0].landmark[9].y and \
                    results.multi_hand_landmarks[0].landmark[16].y < results.multi_hand_landmarks[0].landmark[13].y and \
                    results.multi_hand_landmarks[0].landmark[20].y < results.multi_hand_landmarks[0].landmark[17].y:
                ans = 'paper'

    
handsDetector.close()
