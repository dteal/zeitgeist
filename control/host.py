#!/usr/bin/python3
"""
Master program
"""

import multiprocessing
import pygame
import zmq

class CommProcess(multiprocessing.Process):
    """Communicates with robot."""

    def __init__(self):
        super().__init__(daemon=True)
        self.done = False
        self.speed = 0
        self.steer = 0

    def run(self):
        port = 15787
        context = zmq.Context()
        robot = context.socket(zmq.REQ)
        robot.connect('tcp://zeitgeist.local:{}'.format(port))

        while not self.done:
            robot.send_string('{}:{}'.format(self.speed, self.steer))
            print(robot.recv_string())

def run():

    # both 1000 to -1000
    speed = 0
    steer = 0
    dspeed=100
    dsteer=100

    pygame.init()
    screen = pygame.display.set_mode((500,500))

    robot = CommProcess()

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == 32: # space
                    speed = 0
                    steer = 0
                if event.key == 275 and steer < 1000: # right
                    steer += dsteer
                if event.key == 276 and steer > -1000: # left
                    steer -= dsteer
                if event.key == 273 and speed < 1000: # up
                    speed += dspeed
                if event.key == 274 and speed > -1000: # down
                    speed -= dspeed
            robot.speed = speed
            robot.steer = steer

        screen.fill((0,0,0))
        pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(0, 0, 100, 500))
        pygame.display.flip()

        print('Speed: {}\t Steer: {}'.format(speed, steer))
        #time.sleep(0.02)


if __name__ == "__main__":
    run()
