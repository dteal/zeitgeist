#!/usr/bin/python2
"""Controls Pi on cart."""

import multiprocessing
import time
import numpy as np
import serial
import zmq
import sys
import struct
import freenect
import cv2

class MotorControlProcess(multiprocessing.Process):
    """Send commands to motor control board."""

    def __init__(self, command_queue, sensing_queue, response_queue):
        super(MotorControlProcess, self).__init__()
        self.daemon = True
        self.done = False
        self.queue = command_queue
        self.sensing_queue = sensing_queue
        self.response_queue = response_queue
        self.port = sys.argv[1]
        self.ser = serial.Serial(self.port, 19200)
        print(self.ser)
           
        self.stopped = True
        self.automatic_mode = False
        self.left = 0
        self.right = 0
        self.song = -1

        self.heading = (False, 0)

    def run(self):
        """Continually send control signal."""

        timer = time.time()
        last_command = ''
        last_heading = self.heading

        while not self.done:
            command_flag = False
            try:
                while True:
                    command = self.queue.get(block=False)
                    command_flag = True
            except:
                pass
            if command_flag:
                self.response_queue.put("Received {}".format(command))
                parts = command.split()
                self.stopped = parts[0] == '1'
                self.automatic_mode = parts[1] == '1'
                self.song = int(parts[4])

                if self.automatic_mode:
                    self.response_queue.put("IN AUTO}")
                    try:
                        while True:
                            self.heading = self.sensing_queue.get(block=False)
                            #self.response_queue.put("New heading: {}".format(heading))
                    except:
                        pass

                if self.stopped:
                    self.left = self.right = 0
                else:
                    if not self.automatic_mode:
                        self.response_queue.put("MANUAL")
                        self.left = int(parts[2])
                        self.right = int(parts[3])
                    else:
                        if self.heading[0]:
                            self.response_queue.put("AUTO FOUND")

                            #self.left = 8
                            #self.right = 5
                            #self.left = 8
                            #self.right = -5 
                            #self.left = -8
                            #self.right = 5 

                            self.left = 4
                            self.right = 4

                            self.left += self.heading[1]*4/42.5
                            self.right -= self.heading[1]*4/42.5
                            self.left = round(self.left)
                            self.right = round(self.right)
                        else:
                            self.response_queue.put("AUTO")
                            self.left = self.right = 0

                timer = time.time()
                if (command != last_command) or (time.time() - timer > 0.1) or (self.heading != last_heading):
                    self.write()
                    last_command = command
                    last_heading = self.heading

            else:
                if time.time() - timer > 1:
                    print('Command timeout; stopping robot.')
                    self.stopped = 1
                    self.left = self.right = 0
                    timer = time.time()
                    self.write()

        self.ser.close()

    def write(self):
        """Send steer, speed to board."""
    
        for wheel, velocity in enumerate([self.right,self.left]):
            if wheel == 0:
                wheel = 0x00
            else:
                wheel = 0x02
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
            speed = abs((int)(velocity))
            speed = speed << 3
            result = (wheel | direction | speed)
            checksum = 0
            for i in range(7):
                if (result >> (i+1)):
                    checksum = checksum ^ 0x01
            checksum = checksum ^ 0x01 # invert one more time (for extra robustness against all-zero packets)
            result = result | checksum
            self.ser.write(struct.pack('<B', result))
            print('Serial packet: {:0>8b}\t{}'.format(result, result))

class KinectControlProcess(multiprocessing.Process):
    """Get frame from Kinect."""

    def __init__(self, sensing_queue):
        print('Initializing Kinect thread...')
        super(KinectControlProcess, self).__init__()
        self.daemon = True
        self.done = False
        self.queue = sensing_queue

    def run(self):
        """Continually grab Kinect frames."""
        print('Starting Kinect thread...')
        #camera_port = 15788
        #context = zmq.Context()
        #host = context.socket(zmq.REQ)
        #host.bind('tcp://mesa.local:{}'.format(camera_port))

        color_min_hsv = np.array([25, 32, 128])
        color_max_hsv = np.array([40, 255, 255])

        while not self.done:
            rgb, _ = freenect.sync_get_video()
            #depth, _ = freenect.sync_get_depth()
            rgb = rgb[::8,::8,:]
            hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
            mask = cv2.inRange(hsv, color_min_hsv, color_max_hsv)
            res = cv2.blur(mask, (10,10))
            _, thresh = cv2.threshold(res, 30, 255, cv2.THRESH_BINARY)
            hist = np.sum(thresh, axis=0)
            location = np.argmin(np.abs(np.cumsum(hist)-np.sum(hist)/2))
            presence = np.sum(hist) > 10000
            self.queue.put((presence, location-42.5))
            """
            safe = True
            if presence:
                if safe:
                    print('GO to {}'.format(location-320))
                else:
                    print('OBSTACLE!')
            else:
                print('N/A')
            """


def run():
    """Main loop."""

    sensing_queue = multiprocessing.Queue()
    command_queue = multiprocessing.Queue()
    response_queue = multiprocessing.Queue()
    motor = MotorControlProcess(command_queue, sensing_queue, response_queue)
    kinect = KinectControlProcess(sensing_queue)
    motor.start()
    kinect.start()

    command_port = 15787
    context = zmq.Context()
    host = context.socket(zmq.REP)
    host.bind('tcp://*:{}'.format(command_port))

    done = False
    while not done:
        #print('Waiting for command...')
        command = host.recv_string()

        response = ''
        try:
            response = response_queue.get(block=False)
        except:
            pass

        host.send_string('{}'.format(response))
        #print('Received from host: {}'.format(command))
        command_queue.put(command)

    motor.done = True
    kinect.done = True
    print('Done.')

if __name__ == '__main__':
    run()
