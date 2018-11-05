#!/usr/bin/python3

import serial
import sys

device = sys.argv[1] # /dev/ttyUSB0
device2 = sys.argv[2] # /dev/ttyUSB0
baudrate = 115200 #sys.argv[2]
logfile = sys.argv[3]

def lg(message, out):
    print(message)
    out.write(message)
    out.write('\n')

with open(logfile, 'w') as out:
    lg('Attempting to open serial connection...', out)
    with serial.Serial(device, 115200) as ser:
        lg(ser.__repr__(), out)
        lg('Serial connection 1 opened successfully', out)
        with serial.Serial(device2, 115200) as ser2:
            lg(ser2.__repr__(), out)
            lg('Serial connection 2 opened successfully', out)
            # 9600bad, 19200bad, 38400bad, 57600almost, 115200good
            while True:
                in1 = ser.read(16)
                lg('1: '+in1.hex(), out)
                ser2.write(in1)
                in2 = ser2.read(16)
                lg('2: '+in2.hex(), out)
                ser.write(in2)

