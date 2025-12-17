'''
import cv2

img = cv2.imread("input.png")
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

eps = 0.045 * cv2.arcLength(contours[0], True)
approx = cv2.approxPolyDP(contours[0], eps, True)
print(len(approx))


import cv2

img = cv2.imread('input.png')
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(img, 126,255, cv2.THRESH_BINARY_INV)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

cnt = 0

for i in range(len(hierarchy[0])):
    if hierarchy[0][i][2] == -1 and hierarchy[0][i][3] != -1:
        cnt += 1

print(cnt)
'''

import cv2
import numpy as np

def kvadrat(im):
    s = cv2.contourArea(contours[im])

    eps = 0.045 * cv2.arcLength(contours[0], True)
    approx = cv2.approxPolyDP(contours[0], eps, True)

    if len(approx) != 4 and s < 400:
        return False

    return True

img = cv2.imread("input.png")

imghsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
lower = np.array([23, 50, 100])
upper = np.array([31, 255, 255])
mask = cv2.inRange(imghsv, lower, upper)
img_mask = cv2.bitwise_and(img, img, mask=mask)

contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

ans = 0

for i in range(len(contours)):
    if kvadrat(i):
        ans += 1

print(ans)