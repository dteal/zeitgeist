#!/usr/bin/python2 
"""
This program detects neon yellow.
"""

print('Importing libraries...')
import time
import numpy as np
import freenect
import cv2
import matplotlib.pyplot as plt

if __name__ == '__main__':

    while True:

        print('Analyzing frame...')
        rgb, _ = freenect.sync_get_video()
        rgb = rgb[::8,::8,:]
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        #plt.imshow(hsv); plt.show()
        color_min_hsv = np.array([25, 128, 128])
        color_max_hsv = np.array([35, 255, 255])
        mask = cv2.inRange(hsv, color_min_hsv, color_max_hsv)
        res = cv2.blur(mask, (10,10))
        _, thresh = cv2.threshold(res, 30, 255, cv2.THRESH_BINARY)
        hist = np.sum(thresh, axis=0)
        location = np.argmin(np.abs(np.cumsum(hist)-np.sum(hist)/2))
        presence = np.sum(hist) > 100 # whether there's enough yellow in the image
        print(np.sum(hist))

        print('Ignoring depth!')
        """
        print('Obtaining depth image...')
        def get_depth_frame():
            frame, _ = freenect.sync_get_depth()
            #frame = frame.astype(np.uint8)
            return frame

        # detect obstacles
        depth = get_depth_frame()
        print('Calculating midpoint...')
        mindepths = np.min(depth, axis=0)
        safety_dist = 170
        safe = True
        for i in range(len(mindepths)):
            if mindepths[i] < 500:
                if 320-safety_dist < i < 320 + safety_dist:
                    safe = False
        """
        safe = True

        if presence:
            if safe:
                print('GO to {}'.format(location-320))
            else:
                print('OBSTACLE!')
        else:
            print('N/A')

        if presence:
            cv2.rectangle(bgr, (location,0), (location+1,45), (0,255,0), 2)

        cv2.imshow('image', bgr)
        cv2.imshow('thresh', thresh)


        # exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()



