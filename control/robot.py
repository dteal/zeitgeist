#!/usr/bin/python3
"""Controls Pi on cart."""

import multiprocessing
import freenect
import numpy as np
import serial
import zmq
import queue
import pickle
import time
import sys

class MotorControlProcess(multiprocessing.Process):
    """Send commands to motor control board."""

    def __init__(self, command_queue):
        super().__init__(daemon=True)
        self.done = False
        self.queue = command_queue
        self.left = 0
        self.right = 0
        self.port = sys.argv[1]
        self.ser = serial.Serial(self.port, 19200)
        print(self.ser)

    def run(self):
        """Continually send control signal."""
        while not self.done:
            command_flag = False
            try:
                while True:
                    command = self.queue.get(block=False)
                    command_flag = True
            except queue.Empty:
                pass
            if command_flag:
                if command == 'q':
                    self.left = 0
                    self.right = 0
                    print('Stopping robot.')
                    self.done = True
                else:
                    self.left, self.right = command
                    print('Executing command: {} {}'.format(self.left, self.right))
                self.write()
        self.ser.close()

    def write(self):
        """Send steer, speed to board."""
    
        for wheel, velocity in enumerate([self.right,self.left]):
            #print('=====')
            if wheel == 0:
                wheel = 0x00
            else:
                wheel = 0x02
            #print('wheel: {}'.format(wheel))
            if (int)(velocity) < 0:
                if wheel == 0x02:
                    direction = 0x04
                if wheel == 0x00:
                    direction = 0x00
            else:
                if wheel == 0x02:
                    direction = 0x00
                if wheel == 0x00:
                    direction = 0x04
            #print('dir: {}'.format(direction))
            speed = abs((int)(velocity))
            #print('speed: {}'.format(speed))
            speed = speed << 3
            result = (wheel | direction | speed)
            #print(result.to_bytes(1, byteorder='little', signed=False).hex())
            checksum = 0
            for i in range(7):
                if (result >> (i+1)):
                    checksum = checksum ^ 0x01
            checksum = checksum ^ 0x01 # invert one more time (for extra robustness against all-zero packets)
            #print('checksum: {}'.format(checksum))
            result = result | checksum
            #print(result.to_bytes(1, byteorder='little', signed=False).hex())
            #print(result)
            self.ser.write(result.to_bytes(1, byteorder='little', signed=False))

class KinectControlProcess(multiprocessing.Process):
    """Get frame from Kinect."""

    def __init__(self, image_queue):
        print('Initializing Kinect thread...')
        super().__init__(daemon=True)
        self.done = False
        self.queue = image_queue

    def get_image_frame():
        frame, _ = freenect.sync_get_video()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame

    def get_depth_frame():
        frame, _ = freenect.sync_get_depth()
        #frame = frame.astype(np.uint8)
        return frame

    def run(self):
        """Continually grab Kinect frames."""
        print('Starting Kinect thread...')
        #camera_port = 15788
        #context = zmq.Context()
        #host = context.socket(zmq.REQ)
        #host.bind('tcp://mesa.local:{}'.format(camera_port))
        while not self.done:

            print('Processing image frame...')

            image = get_image_frame()
            # hsv mask
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            color_min_hsv = np.array([172, 128, 128])
            color_max_hsv = np.array([180, 255, 255])
            #color_none_hsv = np.array([0, 128, 128])
            #color_max_hsv = np.array([10, 255, 255])
            #color_min_hsv = np.array([170, 128, 128])
            #color_all_hsv = np.array([180, 255, 255])
            mask = cv2.inRange(hsv, color_min_hsv, color_max_hsv)
            #mask = cv2.inRange(hsv, color_none_hsv, color_max_hsv) + cv2.inRange(hsv, color_min_hsv, color_all_hsv)
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
            x = position[0]; y = position[1]
            infostring = ['Position: ({}, {})'.format(x, y),
                            'HSV: ({:3}, {:3}, {:3})'.format(hsv[y,x,0], hsv[y,x,1], hsv[y,x,2]),
                            'Depth: ({})'.format(depth[y,x])]

            # find object
            if len(newcontours) == 0:
                infostring.append('No object found!')
            else:
                x,y,w,h = cv2.boundingRect(newcontours[maxindex])
                cv2.rectangle(image, (x,y), (x+w,y+h), (0,255,0), 2)

            print('Done processing image frame!')

def run():
    """Main loop."""

    image_queue = multiprocessing.Queue()
    command_queue = multiprocessing.Queue()
    
    motor = MotorControlProcess(command_queue)
    kinect = KinectControlProcess(image_queue)

    motor.start()
    #kinect.start()

    command_port = 15787
    context = zmq.Context()
    host = context.socket(zmq.REP)
    host.bind('tcp://*:{}'.format(command_port))

    done = False
    while not done:
        print('Waiting for command...')
        command = host.recv_string()
        print('Received from host: {}'.format(command))
        host.send_string('ack')

        if command == 'q':
            done = True
            command_queue.put('q')
            print('Exiting...')

        if command[0] == 'c':
            try:
                rates = command.split()
                command_queue.put((int(rates[1]), int(rates[2])))
            except:
                pass

    motor.done = True
    kinect.done = True

    time.sleep(1) # give time for threads to finish

if __name__ == '__main__':
    run()
