# Example file to take images using Point Grey Research camera and use openCV to convert into grey scale
import PyCapture2
import numpy as np
import cv2 

# Connection to camera
bus = PyCapture2.BusManager()
cam = PyCapture2.Camera()

def printNumOfCam():
    """ returns the number of cameras """
    bus = PyCapture2.BusManager()
    numCams = bus.getNumOfCameras()
    print("Number of cameras detected: ", numCams)
    return numCams

def init( camIndex=0 ):
    """
        This function initialises the connection with camera with an index specified by the camIndex parameter and starts the capture process
        WARNING: After init() is called, the camera must be properly closed using .close() method
    """
    print("Initialising connection to camera ", camIndex)
    cam.connect(bus.getCameraFromIndex( camIndex ))
    __printCameraInfo__(cam)
    cam.startCapture()

def setShutter(absValue = 60):
    """ This function sets the shutter value of the camera to manual mode with the specified value"""
    cam.setProperty(type = PyCapture2.PROPERTY_TYPE.SHUTTER, autoManualMode = False, absValue = absValue)

def setGain(absBalue = 15):
    """ This function sets the gain of the camera to manual mode with a specified value"""
    cam.setProperty(type = PyCapture2.PROPERTY_TYPE.GAIN, autoManualMode = False, absValue = absValue)

def setExposure(absValue=1):
    """ This function sets the exposure of the camera to manual mode with a specified value"""
    cam.setProperty(type = PyCapture2.PROPERTY_TYPE.AUTO_EXPOSURE, autoManualMode = False, absValue = absValue)


def capture(display = True, saveRaw = False, saveColorImage = False, saveGreyscaleImage = False):
    """
        This function captures an image and optionally displays the image using openCV.

        If saveRaw is set to True, the raw image is saved to "raw.png"

        If saveColorImage is set to True, the color image is saved to "color.png"

        If saveGreyscaleImage is set to True, the color image is converted into greyscale using OpenCV and saved to "grey.png"

        An CV2 image is returned by the function.
    """
    try:
        # try retrieving the last image from the camera
        rawImg = cam.retrieveBuffer()
        
        bgrImg = rawImg.convert(PyCapture2.PIXEL_FORMAT.BGR)
        # hack for Python3 save the image first and the load it in openCV because the img.getData() method does not work for 
        # the converted image
        bgrImg.save("temp.png".encode(),  PyCapture2.IMAGE_FILE_FORMAT.PNG)

        cvBgrImg = cv2.imread("temp.png")

        if display:
            cv2.imshow('BGR image',cvBgrImg)
            cv2.waitKey()

        # saving images with opencv
        if saveColorImage:
            cv2.imwrite("color.png", cvBgrImg)

        if saveGreyscaleImage:
            # convert to greyscale using opencv library
            cvGreyImg = cv2.cvtColor(cvBgrImg, cv2.COLOR_RGB2GRAY)
            cv2.imwrite("grey.png", cvGreyImg)

        # saving raw image
        if saveRaw:
            rawImg.save("raw.png".encode("utf-8"), PyCapture2.IMAGE_FILE_FORMAT.PNG)
        
        return cvBgrImg
    except PyCapture2.Fc2error as fc2Err:
        print("Error retrieving buffer : ", fc2Err)
        raise RuntimeError("Error retrieving buffer : ", fc2Err)
 



def close():
    """ This function closes the camera connection and stops image capture"""
    cam.stopCapture()
    cam.disconnect()




# Helper functions
def __printCameraInfo__(cam):
	camInfo = cam.getCameraInfo()
	print("\n*** CAMERA INFORMATION ***\n")
	print("Serial number - ", camInfo.serialNumber)
	print("Camera model - ", camInfo.modelName)
	print("Camera vendor - ", camInfo.vendorName)
	print("Sensor - ", camInfo.sensorInfo)
	print("Resolution - ", camInfo.sensorResolution)
	print("Firmware version - ", camInfo.firmwareVersion)
	print("Firmware build time - ", camInfo.firmwareBuildTime)
	print()