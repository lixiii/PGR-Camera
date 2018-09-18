# Point Grey Research Camera Module

This is a Python3 library to control Point Grey Research Cameras.

## Dependencies

- PyCapture2
- OpenCV
- Numbpy

This pacakge depends on the PyCapture2 library provided by Point Grey Research. It must be downloaded and installed *from the Point Grey company website*. 

## Usage

This package comes with a setup script and the pacakage `camera` can be installed using `$ sudo python3 setup.py install`

## Common problems

1. Sometimes the images will suddenly start to contain a lot of noise and the areas that should be dark becomes white noise. In this case, open FlyCap2 and play with the camera settings (mode, pixel format, standard camera modules) until it looks right on the camera. After that disconnect and reconnect the camera and restart whatever script that you are running

