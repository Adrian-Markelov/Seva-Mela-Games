import cv2
import numpy as np
# img = cv2.imread('Ping-pong-OpenCV-master/starfield.png')
# img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# print("img size is {}".format(img.shape))
height = 600
width = 800
img = np.ones((height, width, 3), dtype=np.uint8) * 255


cv2.line(img, (10, 10), (400, 100), (0, 0, 125), 2)
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('image', 700, 500)
cv2.imshow("image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()