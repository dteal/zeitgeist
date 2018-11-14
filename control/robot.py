#!/usr/bin/python3
"""Controls Pi on cart."""

import multiprocessing
import freenect
import numpy as np
import serial
import zmq

class MotorControlProcess(multiprocessing.Process):
    """Send commands to motor control board."""

    def __init__(self):
        super().__init__(daemon=True)
        self.done = False
        self.speed = 0
        self.steer = 0
        self.port = '/dev/ttyUSB0'
        self.ser = serial.Serial(self.port, 19200)
        print(self.ser)

    def run(self):
        """Continually send control signal."""
        while not self.done:
            self.write()
        self.ser.close()

    def write(self):
        """Send steer, speed (both -1000 < x < 1000) to board."""
        self.ser.write(self.speed.to_bytes(2, byteorder='little', signed=True))
        self.ser.write(self.steer.to_bytes(2, byteorder='little', signed=True))
        print('writing!')

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
            print('got frame!')
            self.queue.put(frame)

def run():
    """Main loop."""

    image_queue = multiprocessing.Queue()
    
    motor = MotorControlProcess()
    kinect = KinectControlProcess(image_queue)

    motor.start()
    kinect.start()

    port = 15787
    context = zmq.Context()
    host = context.socket(zmq.REP)
    host.bind('tcp://*:{}'.format(port))

    done = False
    while not done:
        command = host.recv_string()
        print(command)
        if command == 'q':
            done = True
        try:
            frame = image_queue.get(block=False)
            host.send_string('image!: {}'.format(frame.shape))
        except multiprocessing.queue.Empty:
            host.send_string('ack{}'.format(image_queue.qsize())

    motor.done = True
    kinect.done = True

if __name__ == '__main__':
    run()
