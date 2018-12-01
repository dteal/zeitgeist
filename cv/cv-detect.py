#!/usr/bin/python3 
# https://naman5.wordpress.com/2014/06/24/experimenting-with-kinect-using-opencv-python-and-open-kinect-libfreenect/

import freenect
import cv2
import numpy as np

position = [0,0]

def get_image_frame():
    frame, _ = freenect.sync_get_video()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return frame

def get_depth_frame():
    frame, _ = freenect.sync_get_depth()
    #frame = frame.astype(np.uint8)
    return frame

def callback(event, x,y, flags, param):
    global position
    position = [x, y]

if __name__ == '__main__':

    cv2.namedWindow('image')
    cv2.setMouseCallback('image', callback)

    while True:

        # display images
        image = get_image_frame()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        color_min_hsv = np.array([25, 128, 32])
        color_max_hsv = np.array([40, 255, 255])
        mask = cv2.inRange(hsv, color_min_hsv, color_max_hsv)
        res = cv2.bitwise_and(gray, gray, mask=mask)
        res = cv2.blur(res, (10,10))
        ret, thresh = cv2.threshold(res, 30, 255, cv2.THRESH_BINARY)
        _, contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        newcontours = []
        maxarea = 0
        maxindex = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if 50 < cv2.contourArea(contour):
                newcontours.append(contour)
                if area > maxarea:
                    maxarea = area
                    maxindex = len(newcontours)-1

        # detect obstacles
        depth = get_depth_frame()
        mindepths = np.min(depth, axis=0)
        safety_dist = 170
        safe = True
        for i in range(len(mindepths)):
            if mindepths[i] < 500:
                cv2.line(image, (i,0), (i,30), (0,0,255),1)
                if 320-safety_dist < i < 320 + safety_dist:
                    safe = False

        direction = 0
        # find object
        if len(newcontours) == 0:
            pass
        else:
            x,y,w,h = cv2.boundingRect(newcontours[maxindex])
            cv2.rectangle(image, (x,y), (x+w,y+h), (0,255,0), 2)
            direction = x+w/2-320
        if direction == 0:
            safe = False

        # prepare info
        x = position[0]; y = position[1]
        infostring = ['Position: ({}, {})'.format(x, y),
                        'HSV: ({:3}, {:3}, {:3})'.format(hsv[y,x,0], hsv[y,x,1], hsv[y,x,2]),
                        'Depth: ({})'.format(depth[y,x]),
                        'Maxarea: {}'.format(maxarea),
                        'Direction: {}'.format(direction),
                        'GO?: {}'.format(safe)]

        # display info
        for i in range(len(infostring)):
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(image, infostring[i], (10, 470-30*i), font, .7, (255,255,255), 2, cv2.LINE_AA)
           
        #cv2.imshow('Depth', depth)
        cv2.imshow('image', image)
        cv2.imshow('mask', thresh)

        # exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


