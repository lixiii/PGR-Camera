# Example file to take images using Point Grey Research camera and use openCV to convert into grey scale
import PyCapture2
import numpy as np
import cv2 
import time

# Configurations: 
_PIXEL_FORMAT = PyCapture2.PIXEL_FORMAT.RAW16

# Connection to camera
bus = PyCapture2.BusManager()
cam = PyCapture2.Camera()
camInitialised = False

# debug output
# __DEBUG__ = False
__DEBUG__ = True

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
    global camInitialised
    print("Initialising connection to camera ", camIndex)
    cam.connect(bus.getCameraFromIndex( camIndex ))
    __printCameraInfo__(cam)
    # set the format to RAW16 using format 7
    fmt7info, supported = cam.getFormat7Info(0)
    global _PIXEL_FORMAT
    # Check whether pixel format _PIXEL_FORMAT is supported
    if _PIXEL_FORMAT & fmt7info.pixelFormatBitField == 0:
        raise RuntimeError("Pixel format is not supported\n")
    fmt7imgSet = PyCapture2.Format7ImageSettings(0, 0, 0, fmt7info.maxWidth, fmt7info.maxHeight, _PIXEL_FORMAT)
    fmt7pktInf, isValid = cam.validateFormat7Settings(fmt7imgSet)
    if not isValid:
        raise RuntimeError("Format7 settings are not valid!")
    cam.setFormat7ConfigurationPacket(fmt7pktInf.recommendedBytesPerPacket, fmt7imgSet)
    
    cam.startCapture()
    camInitialised = True

def setShutter(absValue = 60):
    """ This function sets the shutter value of the camera to manual mode with the specified value"""
    cam.setProperty(type = PyCapture2.PROPERTY_TYPE.SHUTTER, autoManualMode = False, absValue = absValue)
    return getShutterValue()

def setGain(absValue = 15):
    """ This function sets the gain of the camera to manual mode with a specified value"""
    cam.setProperty(type = PyCapture2.PROPERTY_TYPE.GAIN, autoManualMode = False, absValue = absValue)
    return getGainValue()

def setExposure(absValue=1):
    """ This function sets the exposure of the camera to manual mode with a specified value"""
    cam.setProperty(type = PyCapture2.PROPERTY_TYPE.AUTO_EXPOSURE, autoManualMode = False, absValue = absValue)
    return cam.getProperty( PyCapture2.PROPERTY_TYPE.AUTO_EXPOSURE ).absValue

def setFramerate(absValue=30):
    """ This function sets the framrate and returns the value from the camera as it will not be exact """
    cam.setProperty(type = PyCapture2.PROPERTY_TYPE.FRAME_RATE, autoManualMode = False, absValue = absValue)
    return getFramerate()

def autoAdjust():
    """ Set the camera to auto mode for all settings """
    cam.setProperty(type = PyCapture2.PROPERTY_TYPE.AUTO_EXPOSURE, autoManualMode = True)
    cam.setProperty(type = PyCapture2.PROPERTY_TYPE.GAIN, autoManualMode = True)
    cam.setProperty(type = PyCapture2.PROPERTY_TYPE.SHUTTER, autoManualMode = True)
    cam.setProperty(type = PyCapture2.PROPERTY_TYPE.FRAME_RATE, autoManualMode = True)

def getShutterValue():
    """ Returns the current shutter value """
    return cam.getProperty( PyCapture2.PROPERTY_TYPE.SHUTTER ).absValue

def getGainValue():
    """ Returns the current gain value """
    return cam.getProperty( PyCapture2.PROPERTY_TYPE.GAIN ).absValue

def getFramerate():
    return cam.getProperty( PyCapture2.PROPERTY_TYPE.FRAME_RATE ).absValue

def capture(display = True, returnGreyImage = False, saveRaw = False, saveColorImage = False, saveGreyscaleImage = False, 
            rawImgName = "raw.png", colorImgName = "color.png", greyImgName="grey.png"):
    """
        This function captures an image and optionally displays the image using openCV.

        If returnGreyImage is set to True, the returned cv2 image will be the image after greyscale conversion. 

        If saveRaw is set to True, the raw image is saved to "raw.png" (default file name)

        If saveColorImage is set to True, the color image is saved to "color.png" (default file name)

        If saveGreyscaleImage is set to True, the color image is converted into greyscale using OpenCV and saved to "grey.png" (default file name)

        An CV2 image is returned by the function.
    """
    if not camInitialised:
        raise RuntimeError("Camera not initialised. Please intialise with init() method")
    try:
        # try retrieving the last image from the camera
        rawImg = cam.retrieveBuffer()
        
        bgrImg = rawImg.convert(PyCapture2.PIXEL_FORMAT.BGR16)
        # hack for Python3 save the image first and the load it in openCV because the img.getData() method does not work for 
        # the converted image
        bgrImg.save("temp.png".encode(),  PyCapture2.IMAGE_FILE_FORMAT.PNG)

        cvBgrImg = cv2.imread("temp.png",-1) # -1 for no conversion to 8 bits

        if display:
            cv2.imshow('BGR image',cvBgrImg)
            cv2.waitKey()

        # saving images with opencv
        if saveColorImage:
            cv2.imwrite(colorImgName, cvBgrImg)

        if saveGreyscaleImage or returnGreyImage:
            # convert to greyscale using opencv library
            cvGreyImg = cv2.cvtColor(cvBgrImg, cv2.COLOR_RGB2GRAY)

            if saveGreyscaleImage:
                cv2.imwrite(greyImgName, cvGreyImg)

        # saving raw image
        if saveRaw:
            rawImg.save(rawImgName.encode("utf-8"), PyCapture2.IMAGE_FILE_FORMAT.PNG)
        
        if returnGreyImage:
            return cvGreyImg
        else:
            return cvBgrImg
    except PyCapture2.Fc2error as fc2Err:
        print("Error retrieving buffer : ", fc2Err)
        raise RuntimeError("Error retrieving buffer : ", fc2Err)
 
def isSaturated(greyConversion = False, findIndices = False):
    """
        This function captures an image and checks all the pixels to see if any pixel is saturated. 
        
        If greyConversion is True, this function converts the image into a greyscale image and checks for saturation using the greyscale image. 

        If findIndices is set to True, a tuple indicating the first saturated pixel is also returned if the image is saturated. 
    """
    if not camInitialised:
        raise RuntimeError("Camera not initialised. Please intialise with init() method")
    img = capture( False, greyConversion )
    # smooth the image over kernal of (3,3)
    img = cv2.blur(img, (3, 3))
    if __DEBUG__:
        cv2.imshow("blurred", img)
        cv2.waitKey(500)
    
    # then check the image pixel bit size:
    if img.dtype.itemsize == 2:
        PIX_MAX = 65535
    elif img.dtype.itemsize == 1:
        PIX_MAX = 255
    else:
        raise RuntimeError("Pixel size not supported. Please add pixel max. ")
    if np.amax( img ) == PIX_MAX:
        if findIndices:
            indices = np.unravel_index(np.argmax(img, axis=None), img.shape)
            return True, indices
        else:
            return True
    else:
        return False

def adjustShutter(maxIteration = 20, stepSize = 5, verbose = True, camAutoAdjust = True, gainOffset = 0, initShutterOffset = 0):
    """
        This function automatically adjusts the shutter to a level where the brightest pixel is just below saturation. 

        Iteration variables: 
        MaxIteration    - maximum iteration limit
        stepSize        - the step size to decrease the shutter value
        verbose         - prints the iteration progress
        camAutoAdjust      - If this is set to false, the routine will NOT use auto adjustment at the start. Change this to false only when you know 
                            what you are doing
        gainOffset      - The gain is set by the camera's auto adjustment and to achieve a higher dynamic range, a lower gain is usually desired. 
                            Hence, set the offset to a small value like 0.5 --- 5 if the dynamic range is not sufficient or if the adjustment fails. 
                            This is a negative offset, ie the programme reduces this amount from the initGain value
        initShutterOfffet - To account for the gain offset, the starting shutter needs to be larger and hence this is a positive offset. 
    """
    if not camInitialised:
        raise RuntimeError("Camera not initialised. Please intialise with init() method")
    if camAutoAdjust:
        if verbose:
            print("enabling auto adjustment mode and waiting for camera to adjust settings")
        autoAdjust()
        time.sleep(2)

    initGain = getGainValue() - gainOffset
    setGain(initGain)
    time.sleep(1) # wait for readjustment as gain is set
    initShutter = getShutterValue() + initShutterOffset
    if verbose:
        print("Camera adjustment completed. Disabling the auto adjustment modes. \nCurrent gain = " + str(initGain) + " and shutter = " + str(initShutter))

    shutterValue = initShutter
    setShutter(initShutter)

    for i in range(maxIteration):
        sat = isSaturated()
        if sat:
            shutterValue = shutterValue - stepSize
            if shutterValue <= 0:
                raise RuntimeError("Shutter value has exceeded minimum possible value. You can retry with a smaller step size. ")
                break
            setShutter( shutterValue )
            printIterationStatus(i + 1, shutterValue, sat, verbose)
        else:
            printIterationStatus(i + 1, shutterValue, sat, verbose)
            break
    
    return sat
 
def autoAdjustShutter(iterationLimit = 100, verbose = True):
    """
        This function calls the iteration routine adjustShutter automatically and changes the gain and iteration variables until a maximum iteration limit OR until saturation = False
        iterationLimit refers to the maximum iteration steps.
    """
    i = 0
    # Each adjustShutter call takes 10 maximum steps
    adjustLimit = iterationLimit / 10
    # get most negative gain    
    minGain = setGain(1)
    for testGain in range(0, -10, -1):
        current = setGain(testGain)
        if current < minGain:
            minGain = current
    if not camInitialised:
        raise RuntimeError("Camera not initialised. Please intialise with init() method")
    if verbose:
        print("enabling auto adjustment mode and waiting for camera to adjust settings")
        print("Camera minimum gain = " + str(minGain) )
    autoAdjust()
    time.sleep(2)
    initGain = getGainValue()
    initShutter = getShutterValue()
    gainStep = (initGain - minGain) / 10

    while i < adjustLimit:
        i = i + 1
        newGain = setGain(initGain - gainStep * i)
        if verbose:
            print("Trying another iteration with gain: " + str( newGain ))
        step = ( setShutter(initShutter) - 0.001 )/ 10
        sat = adjustShutter(10, step, verbose, False)
        if sat == False:
            return False
    
    if sat:
        raise RuntimeWarning("Shutter optimisation failed. Try with larger limit.")
    return sat



def captureAverage( frameCount = 10, display=False, greyScale = False ):
    """
        This function captures the specified number of frames and averages them as they are captured. 
        If display = True, the final averaged image is displayed. 
        If greyScale = True, greyscale images will be used.
    """
    img = capture(False, returnGreyImage =  greyScale)
    for i in range(frameCount):
        tempImg = capture(False, returnGreyImage =  greyScale)
        img = cv2.addWeighted(img, 0.5, tempImg, 0.5, 0)
        if __DEBUG__:
            cv2.imshow(str(i), tempImg)
            cv2.imshow("img"+str(i), img)

    if display:
        cv2.imshow("Averaged over " + str(frameCount) + " frames",img)
        cv2.waitKey()
    return img

def close():
    """ This function closes the camera connection and stops image capture"""
    global camInitialised
    camInitialised = False
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


def printIterationStatus(itCount, shutterValue, sat, verbose):
    if verbose:
        print("-------------------------------")
        print("Iteration " + str(itCount) + " :")
        print("Shutter: " + str(shutterValue) + " , Saturated: " + str(sat))
