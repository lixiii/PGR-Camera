# An example using openCV to process the image captured
import camera
import cv2

camera.init(0)
img = camera.capture(False)
camera.close()

cv2.imshow("image",img)
cv2.waitKey()
