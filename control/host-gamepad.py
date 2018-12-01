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

    def __init__(self, command_queue):
        super().__init__(daemon=True)
        self.done = False
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
                robot.send_string(command)
                print("Sent to robot: {}".format(command))
                response = robot.recv_string()
                print("Received from robot: {}".format(response))

def run():

    stopped = True
    fast_mode = False
    automatic_mode = False
    left_speed = 0
    right_speed = 0
    max_speed_slow = 16.0
    max_speed_fast = 31.0
    song = -1
    
    pygame.init()
    screen = pygame.display.set_mode((1024,768))
    pygame.joystick.init()

    command_queue = multiprocessing.Queue()
    robot = CommProcess(command_queue)
    robot.start()

    timer = time.time()

    done = False
    while not done:
        joy = pygame.joystick.Joystick(0)
        joy.init()
        flag = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.unicode == 'q':
                    done = True
                    break
            if event.type == pygame.QUIT:
                done = True
                break
            if event.type == pygame.JOYBUTTONDOWN:
                button = event.button
                if button == 6 or button == 7:
                    print('Stopped.')
                    stopped = True
                    flag = True
                if button == 4 or button == 5:
                    if joy.get_button(4) == joy.get_button(5) == 1:
                        print('Fast mode enabled.')
                        fast_mode = True
                        flag = True
                if button == 8: # turn on automatic
                    print('Automatic on.')
                    automatic_mode = True
                    flag = True
                if button == 9: # turn on manual
                    print('Manual on.')
                    automatic_mode = False
                    flag = True
                if 0 <= button <= 3:
                    print('Song {} selected.'.format(button))
                    song = button
                    flag = True
            if event.type == pygame.JOYBUTTONUP:
                button = event.button
                if button == 6 or button == 7:
                    if joy.get_button(6) == joy.get_button(7) == 0:
                        print('Unstopped.')
                        stopped = False
                        flag = True
                if button == 4 or button == 5:
                    print('Fast mode disabled.')
                    fast_mode = False
                    flag = True
                if 0 <= button <= 3:
                    if joy.get_button(0) == joy.get_button(1) == joy.get_button(2) == joy.get_button(3) == 0:
                        song = -1
                        flag = True
        old_left = left_speed
        old_right = right_speed
        left_speed = -joy.get_axis(1)
        right_speed = -joy.get_axis(3)
        if fast_mode:
            left_speed *= max_speed_fast
            right_speed *= max_speed_fast
        else:
            left_speed *= max_speed_slow
            right_speed *= max_speed_slow
        left_speed = round(left_speed)
        right_speed = round(right_speed)

        if flag or old_left != left_speed or old_right != right_speed or time.time()-timer > 0.05:
            command_queue.put('c {} {} {} {} {}'.format({True:1,False:0}[stopped], {True:1,False:0}[automatic_mode], left_speed, right_speed, song))
            timer = 0

        screen.fill((255, 255, 255))
        pygame.display.flip()

    #time.sleep(1) # allow time for threads to finish

if __name__ == "__main__":
    run()
