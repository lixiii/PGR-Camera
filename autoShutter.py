# Example script to automatically set the shutter such that the brightest pixel is just below saturation

import camera as cam

cam.init()
cam.autoAdjustShutter()

# Finally
cam.capture()
cam.close()

