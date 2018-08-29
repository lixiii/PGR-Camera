# Example script to automatically set the shutter such that the brightest pixel is just below saturation

import camera as cam

cam.init()
cam.adjustShutter()

# Finally
cam.capture()
cam.close()

