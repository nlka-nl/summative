import cv2
import numpy as np

'''
I

img = cv2.imread("input.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
avg = np.mean(gray)
tr = np.where(gray < avg, 255, 0)
cv2.imwrite("output.png", tr)
'''
img = cv2.imread("input.png")
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

if contours:
    largest_contour = max(contours, key=cv2.contourArea)

    # Аппроксимируем контур полигоном
    epsilon = 0.02 * cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, epsilon, True)

    # Количество вершин
    num_vertices = len(approx)

    print(num_vertices)
