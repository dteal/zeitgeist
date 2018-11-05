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
        # 9600, 19200, 38400, 115200
        lg(ser.__repr__(), out)
        lg('Serial connection opened successfully', out)
        while True:
            #ser.write(b'aa0100000000000000000000000000ab')
            #lg(ser.read(16).hex(), out)
            #ser.write(b'aa01000000000000e404dc0400000073')
            ser.write(b'aa01000000110000ea04e20400000090')
            ser.write(b'aa08000000120000eb04e20400000099')
