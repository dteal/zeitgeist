#!/usr/bin/python2 
# https://naman5.wordpress.com/2014/06/24/experimenting-with-kinect-using-opencv-python-and-open-kinect-libfreenect/

print('Importing libraries...')
import freenect
import cv2
import numpy as np
import time

def get_image_frame():
    return frame

def get_depth_frame():
    frame, _ = freenect.sync_get_depth()
    #frame = frame.astype(np.uint8)
    return frame

def callback(event, x,y, flags, param):
    global position
    position = [x, y]

if __name__ == '__main__':

    while True:

        print('Analyzing frame...')
        rgb, _ = freenect.sync_get_video()
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        #gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        color_min_hsv = np.array([25, 128, 32])
        color_max_hsv = np.array([40, 255, 255])
        mask = cv2.inRange(hsv, color_min_hsv, color_max_hsv)
        #res = cv2.bitwise_and(gray, gray, mask=mask)
        res = cv2.blur(mask, (10,10))
        #res = cv2.blur(res, (10,10))
        ret, thresh = cv2.threshold(res, 30, 255, cv2.THRESH_BINARY)
        hist = np.sum(thresh, axis=0)
        #presence = np.sum(hist) > 100 # whether there's enough yellow in the image
        location = np.argmin(np.abs(np.cumsum(hist)-np.sum(hist)/2))

        """
        hsv = mpl.colors.rgb_to_hsv(rgb)
        print('Frame: {}'.format(rgb.shape))
        print('Masking...')
        hue_mask = np.ma.masked_inside(hsv[:,:,0], 25/180, 40/180).mask
        sat_mask = np.ma.masked_inside(hsv[:,:,1], 128/255, 255/255).mask
        val_mask = np.ma.masked_inside(hsv[:,:,2], 32/255, 255/255).mask
        masked = np.zeros((480, 640))
        masked[np.logical_and(np.logical_and(hue_mask, sat_mask), val_mask)] = 1

        print('Masked: {}'.format(masked.shape))
        print('Blurring...')
        blur = flt.gaussian_filter(masked, sigma=10)
        print('Blur: {}'.format(blur.shape))
        print('Thresholding...')
        thresh = np.ma.masked_inside(blur, 30/255, 255/255).mask
        print('Thresh: {}'.format(thresh.shape))
        tracked = np.zeros((480, 640))
        tracked[thresh] = 1
        #plt.imshow(tracked); plt.show()
        print('Calculating location...')
        hist = np.sum(tracked, axis=0)
        presence = np.sum(hist) > 100 # whether there's enough yellow in the image
        """
        #plt.plot(hist); plt.show()

        print('Ignoring depth!')
        """
        print('Obtaining depth image...')
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

        if True:
            if safe:
                print('GO to {}'.format(location-320))
            else:
                print('OBSTACLE!')
        else:
            print('N/A')

