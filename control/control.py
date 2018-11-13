#!/usr/bin/python3

import sys
import time
import serial
import pygame

port = sys.argv[1]

# both 1000 to -1000
speed = 0
steer = 0

dspeed=100
dsteer=100

if __name__ == "__main__":
    print('Attempting to open serial connection...')
    with serial.Serial(sys.argv[1], 19200) as ser:
        print(ser)
        print('Serial connection opened successfully')
        pygame.init()
        screen = pygame.display.set_mode((500,500))
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.KEYDOWN:
                    if event.key == 32:
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
            screen.fill((0,0,0))
            pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(0, 0, 100, 500))
            pygame.display.flip()

            print('Speed: {}\t Steer: {}'.format(speed, steer))
            ser.write(speed.to_bytes(2, byteorder='little', signed=True))
            ser.write(steer.to_bytes(2, byteorder='little', signed=True))
            #time.sleep(0.02)
