# This code does the following:
# 1. Load a frame of the video from an img file
# 2. Crop down the middle (to separate left and right tablas)
# 3. Do some edge detection to isolate the hand
# ~nikhil jan 16 2019
import cv2
import numpy as np

# 1. Load the image
img = cv2.imread('test2_input.png', cv2.IMREAD_GRAYSCALE)

# 2. Crop down the middle
img_width, img_height = img.shape[1], img.shape[0]
left_tabla_img = img[0:img_height, 0: int(img_width / 2)]
right_tabla_img = img[0:img_height, int(img_width / 2):img_width]

# 3. Edge detection to isolate the hand
left_out = cv2.Canny(left_tabla_img,0,200)
right_out = cv2.Canny(right_tabla_img,50,200)

# Optional: display the final processed imgs 
cv2.namedWindow('left',cv2.WINDOW_NORMAL)
cv2.imshow("left", left_out)

cv2.namedWindow('right',cv2.WINDOW_NORMAL)
cv2.imshow("right", right_out)

cv2.imwrite('test2_out_left.png', left_out)
cv2.imwrite('test2_out_right.png', right_out)

cv2.waitKey(0)
cv2.destroyAllWindows()
