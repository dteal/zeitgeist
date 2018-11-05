#!/usr/bin/python3

import serial
import sys

device = sys.argv[1] # /dev/ttyUSB0
baudrate = 115200 #sys.argv[2]
logfile = sys.argv[2]

def lg(message, out):
    print(message)
    out.write(message)
    out.write('\n')

with open(logfile, 'w') as out:
    lg('Attempting to open serial connection...', out)
    with serial.Serial(sys.argv[1], 115200) as ser:
        # 9600bad, 19200bad, 38400bad, 57600almost, 115200good
        lg(ser.__repr__(), out)
        lg('Serial connection opened successfully', out)
        while True:
            lg(ser.read(16).hex(), out)
