# Example file to take images using Point Grey Research camera and use openCV to convert into grey scale
import PyCapture2
import util
import numpy as np
import cv2 

util.printNumOfCam()

# Connection to camera
bus = PyCapture2.BusManager()
cam = PyCapture2.Camera()
cam.connect(bus.getCameraFromIndex( 1 ))

# print camera info
util.printCameraInfo(cam)

# Camera Settings
cam.setProperty(type = PyCapture2.PROPERTY_TYPE.SHUTTER, autoManualMode = False, absValue = 60)
cam.setProperty(type = PyCapture2.PROPERTY_TYPE.GAIN, autoManualMode = False, absValue = 15)
cam.setProperty(type = PyCapture2.PROPERTY_TYPE.AUTO_EXPOSURE, autoManualMode = False, absValue = 1)

cam.startCapture()

try:
    # try retrieving the last image from the camera
    rawImg = cam.retrieveBuffer()
    
    bgrImg = rawImg.convert(PyCapture2.PIXEL_FORMAT.BGR)
    # hack for Python3 save the image first and the load it in openCV because the img.getData() method does not work for 
    # the converted image
    bgrImg.save("temp.png".encode(),  PyCapture2.IMAGE_FILE_FORMAT.PNG)

    cvBgrImg = cv2.imread("temp.png")
    cv2.imshow('BGR image',cvBgrImg)

    # convert to greyscale using opencv library
    cvGreyImg = cv2.cvtColor(cvBgrImg, cv2.COLOR_RGB2GRAY)
    cv2.imshow("grey", cvGreyImg)

    # saving images with opencv
    cv2.imwrite("color.png", cvBgrImg)
    cv2.imwrite("grey.png", cvGreyImg)

    # saving raw image
    rawImg.save("raw.png".encode("utf-8"), PyCapture2.IMAGE_FILE_FORMAT.PNG)
    
except PyCapture2.Fc2error as fc2Err:
    print("Error retrieving buffer : ", fc2Err)

cam.stopCapture()
cam.disconnect()

# keep opencv images open until key press
cv2.waitKey(0)
