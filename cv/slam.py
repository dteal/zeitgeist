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

    depths1 = np.zeros((50))
    depths2 = np.zeros((50))
    depths3 = np.zeros((50))

    while True:

        # display images
        image = get_image_frame()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        #color_min_hsv = np.array([172, 128, 128])
        #color_max_hsv = np.array([180, 255, 255])
        color_none_hsv = np.array([0, 128, 128])
        color_max_hsv = np.array([10, 255, 255])
        color_min_hsv = np.array([170, 128, 128])
        color_all_hsv = np.array([180, 255, 255])
        #mask = cv2.inRange(hsv, color_min_hsv, color_max_hsv)
        # 480 x 640 x 3
        mask = cv2.inRange(hsv, color_none_hsv, color_max_hsv) + cv2.inRange(hsv, color_min_hsv, color_all_hsv)
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

        # detect obstacles
        depth = get_depth_frame()
        mindepths = np.min(depth, axis=0)
        for i in range(len(mindepths)):
            if mindepths[i] < 600:
                cv2.line(image, (i,0), (i,30), (0,0,255),1)

        # prepare info
        depths1 = np.roll(depths1, 1)
        depths2 = np.roll(depths2, 1)
        depths3 = np.roll(depths3, 1)
        depths1[0] = np.average(depth[230:250,310:330])
        depths2[0] = np.average(depth[230:250,465:485])
        depths3[0] = np.average(depth[230:250,520:540])
        x = position[0]; y = position[1]
        infostring = ['Position: ({}, {})'.format(x, y),
                        'HSV: ({:3}, {:3}, {:3})'.format(hsv[y,x,0], hsv[y,x,1], hsv[y,x,2]),
                        'Depth: ({})'.format(depth[y,x]),
                        'Average Depth 1: ({})'.format(np.mean(depths1)),
                        'Average Depth 2: ({})'.format(np.mean(depths2)),
                        'Average Depth 3: ({})'.format(np.mean(depths3))]
        cv2.rectangle(image, (310,230), (330,250), (0,0,255), 2)
        cv2.rectangle(image, (465,230), (485,250), (0,0,255), 2)
        cv2.rectangle(image, (520,230), (540,250), (0,0,255), 2)

        # find object
        if len(newcontours) == 0:
            infostring.append('No object found!')
        else:
            x,y,w,h = cv2.boundingRect(newcontours[maxindex])
            cv2.rectangle(image, (x,y), (x+w,y+h), (0,255,0), 2)

        # display info
        for i in range(len(infostring)):
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(image, infostring[i], (10, 470-30*i), font, .7, (255,255,255), 2, cv2.LINE_AA)
           
        #cv2.imshow('Depth', depth)
        cv2.imshow('image', image)
        cv2.imshow('depth', depth.astype(np.int8))
        # exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


