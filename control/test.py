#!/usr/bin/python3
"""Command-line hoverboard drive tester.

Commands:
    
    r (speed)
    l (speed)
    q

"""

import sys
import time
import serial

def clamp(n, min, max):
    if n < min:
        return min
    if n > max:
        return max
    return n

#ser.write(speed.to_bytes(2, byteorder='little', signed=True))

if __name__ == "__main__":
    print('Attempting to open serial connection...')
    with serial.Serial(sys.argv[1], 19200) as ser:
        print(ser)
        print('Serial connection opened successfully')
        done = False

        speedr = 0
        speedl = 0

        while not done:
            command = input(">>> ").split()
            if command[0] == 'q':
                done = True
            if command[0] == 'r' or command[0] == 'l':
                print('===')
                if command[0] == 'r':
                    wheel = 0x00
                else:
                    wheel = 0x02
                print('wheel: {}'.format(wheel))
                if (int)(command[1]) < 0:
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
                speed = clamp(abs((int)(command[1])), 0, 31)
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
                ser.write(result.to_bytes(1, byteorder='little', signed=False))

