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
            print('=====')
            if wheel == 0:
                wheel = 0x00
            else:
                wheel = 0x02
            print('wheel: {}'.format(wheel))
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
            print('dir: {}'.format(direction))
            speed = abs((int)(velocity))
            print('speed: {}'.format(speed))
            speed = speed << 3
            result = (wheel | direction | speed)
            print(result.to_bytes(1, byteorder='little', signed=False).hex())
            checksum = 0
            for i in range(7):
                if (result >> (i+1)):
                    checksum = checksum ^ 0x01
            checksum = checksum ^ 0x01 # invert one more time (for extra robustness against all-zero packets)
            print('checksum: {}'.format(checksum))
            result = result | checksum
            print(result.to_bytes(1, byteorder='little', signed=False).hex())
            print(result)
            self.ser.write(result.to_bytes(1, byteorder='little', signed=False))

class KinectControlProcess(multiprocessing.Process):
    """Get frame from Kinect."""

    def __init__(self, image_queue):
        super().__init__(daemon=True)
        self.done = False
        self.queue = image_queue

    def run(self):
        """Continually grab Kinect frames."""
        while not self.done:
            frame, _ = freenect.sync_get_video()
            self.queue.put('got frame!')

def run():
    """Main loop."""

    #image_queue = multiprocessing.Queue()
    command_queue = multiprocessing.Queue()
    
    motor = MotorControlProcess(command_queue)
    #kinect = KinectControlProcess(image_queue)

    motor.start()
    #kinect.start()

    port = 15787
    context = zmq.Context()
    host = context.socket(zmq.REP)
    host.bind('tcp://*:{}'.format(port))

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

        """
        try:
            status = image_queue.get(block=False)
            host.send_string(status)
        except queue.Empty:
            host.send_string('ack / {}'.format(image_queue.qsize()))
        """

    motor.done = True
    #kinect.done = True

    time.sleep(1) # give time for threads to finish

if __name__ == '__main__':
    run()
