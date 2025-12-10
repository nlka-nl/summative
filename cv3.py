import cv2
import numpy as np

'''
image = cv2.imread('input.png')
p = np.array(image)
p[:, :, 1] = 0
p[:, :, 0] = 0
cv2.imwrite('output.png', p)


image = cv2.imread('rose.jpg')
image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

lower1 = np.array([0, 100, 20])
upper1 = np.array([10, 255, 255])
lower2 = np.array([160, 100, 20])
upper2 = np.array([179, 255, 255])

mask1 = cv2.inRange(image_hsv, lower1, upper1)
mask2 = cv2.inRange(image_hsv, lower2, upper2)

full_mask = mask1 + mask2

image_masked = cv2.bitwise_and(image, image, mask=full_mask)
'''

def threshold(_):
    #ret, th = cv2.threshold(img_orig, cv2.getTrackbarPos('Threshold', 'Threshold demo'), 255, cv2.THRESH_BINARY)
    #cv2.imshow("Threshold demo", th)
    imgcopy = img_orig.copy()
    img = cv2.cvtColor(imgcopy, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, (612, 317))
    ret, img = cv2.threshold(img, cv2.getTrackbarPos('Threshold', 'Threshold demo'), 255, cv2.THRESH_BINARY)

    img = cv2.blur(img, (5, 5))
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        eps = 0.1 * cv2.arcLength(cnt, True)
        cnt = cv2.approxPolyN(cnt, eps, True)
        cv2.drawContours(imgcopy, [cnt], -1, (255, 0, 0), 1)

    cv2.drawContours(imgcopy, contours, -1, (0, 255, 0), 1)
    # в начале программы видим исходное изображение
    cv2.imshow("Threshold demo", imgcopy)
    cv2.imshow("Original", img)

    print(contours)

img_orig=cv2.imread("input.png")
cv2.imshow("Threshold demo", img_orig)

cv2.createTrackbar('Threshold','Threshold demo', 0, 255, threshold)

cv2.waitKey(0)
