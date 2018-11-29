#!/usr/bin/python3
"""
Master program """

import multiprocessing
import math
import queue
import time
import pickle
import numpy as np
import pygame
import zmq

class CommProcess(multiprocessing.Process):
    """Communicates with robot."""

    def __init__(self, image_queue, command_queue):
        super().__init__(daemon=True)
        self.done = False
        self.image_queue = image_queue
        self.command_queue = command_queue

    def run(self):
        port = 15787
        context = zmq.Context()
        robot = context.socket(zmq.REQ)
        robot.connect('tcp://zeitgeist.local:{}'.format(port))

        while not self.done:
            command_flag = False
            try:
                while True:
                    command = self.command_queue.get(block=False)
                    command_flag = True
            except queue.Empty:
                pass
            if command_flag:
                if not len(command) == 2:
                    self.done = True
                    break
                robot.send_string('c {} {}'.format(command[0], command[1]))
                print("Sent to robot: {}".format(command))
                response = robot.recv_string()
                print("Received from robot: {}".format(response))

        robot.send_string('q')
        robot.recv_string()

def run():

    # current speeds
    left = 0
    right = 0
    # speed factor (left and right can be +/- 31 max)
    speed = 16.0
    # screen radius
    size = 250
    # deadzone size
    deadzone = 10
    # motors on
    enabled = True
    
    pygame.init()
    screen = pygame.display.set_mode((2*size, 2*size))

    image_queue = multiprocessing.Queue()
    command_queue = multiprocessing.Queue()
    robot = CommProcess(image_queue, command_queue)
    robot.start()

    done = False
    while not done:
        old_left = left
        old_right = right
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                command_queue.put('q')
            if event.type == pygame.MOUSEMOTION:
                x = event.pos[0]-size
                y = -(event.pos[1]-size)
                if x**2+y**2 < deadzone**2:
                    left = 0
                    right = 0
                else:
                    left = right = speed*y/size
                    left += speed*x/size
                    right -= speed*x/size
                    left = int(left)
                    right = int(right)
            if event.type == pygame.KEYDOWN:
                if event.key == 32: # space
                    enabled = not enabled
                    left = 0
                    right = 0
        if(old_left != left or old_right != right):
            print('GUI sensed movement: ({},{}):\t{}\t{}'.format(x, y, left, right))
            command_queue.put((left, right))
        """
        try:
            image = image_queue.get(block=False)
            print(image.shape)
        except queue.Empty:
            pass
        """
        if enabled :
            screen.fill((0, 0, 0))
            pygame.draw.circle(screen, (255, 255, 0), (size, size), deadzone)
        else:
            screen.fill((255, 255, 255))
        pygame.display.flip()
    time.sleep(1) # allow time for threads to finish

if __name__ == "__main__":
    run()
