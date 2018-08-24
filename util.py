# Helper functions for PyCapture2
import PyCapture2

def printCameraInfo(cam):
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

def printNumOfCam():
    bus = PyCapture2.BusManager()
    numCams = bus.getNumOfCameras()
    print("Number of cameras detected: ", numCams)
    if not numCams:
        print("Insufficient number of cameras. Exiting...")
