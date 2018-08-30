# Example using the camera module
import camera
import cv2
camera.printNumOfCam()
camera.init(0)
camera.capture()
print("Checking if the image is saturated. Saturation status: " + str( camera.isSaturated( False, True ) ) )
print("Framerate = " + str( camera.setFramerate(30) ) )
print("Averaging frames")
img = camera.captureAverage(100, True)
cv2.imwrite("averaged.png", img)
camera.close()
