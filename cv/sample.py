#!/usr/bin/python3 
# https://naman5.wordpress.com/2014/06/24/experimenting-with-kinect-using-opencv-python-and-open-kinect-libfreenect/

import freenect
import numpy as np

position = [0,0]

def get_image_frame():
    frame, _ = freenect.sync_get_video()
    return frame

if __name__ == '__main__':

    image = get_image_frame()
    print(image)

