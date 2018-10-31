#!/usr/bin/python3 
# https://naman5.wordpress.com/2014/06/24/experimenting-with-kinect-using-opencv-python-and-open-kinect-libfreenect/

import freenect
import cv2
import numpy as np

def get_image_frame():
    frame, _ = freenect.sync_get_video()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return frame

def get_depth_frame():
    frame, _ = freenect.sync_get_depth()
    frame = frame.astype(np.uint8)
    return frame

if __name__ == '__main__':
    while True:

        # display images
        image = get_image_frame()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        color_min_hsv = np.array([172, 128, 128])
        color_max_hsv = np.array([180, 255, 255])
        mask = cv2.inRange(hsv, color_min_hsv, color_max_hsv)
        res = cv2.bitwise_and(gray, gray, mask=mask)
        res = cv2.blur(res, (40,40))
        ret, thresh = cv2.threshold(res, 10, 255, cv2.THRESH_BINARY)
        _, contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        newcontours = []
        maxarea = 0
        maxindex = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if 2000 < cv2.contourArea(contour) < 200000:
                newcontours.append(contour)
                if area > maxarea:
                    maxarea = area
                    maxindex = len(newcontours)-1

        if len(newcontours) == 0:
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(image, 'No object found!', (10, 30), font, 1, (255,255,255), 2, cv2.LINE_AA)
        else:
            x,y,w,h = cv2.boundingRect(newcontours[maxindex])
            cv2.rectangle(image, (x,y), (x+w,y+h), (0,255,0), 2)
            

        depth = get_depth_frame()
        #cv2.imshow('RGB', image)
        cv2.imshow('mask', image)
        #cv2.imshow('Depth', depth)

        # exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


