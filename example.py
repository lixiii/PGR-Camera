# Example using the camera module
import camera
camera.printNumOfCam()
camera.init(0)
camera.capture()
print("Checking if the image is saturated. Saturation status: " + str( camera.isSaturated( False, True ) ) )
camera.close()