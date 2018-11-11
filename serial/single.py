#!/usr/bin/python3
"""
This program prints 16-byte messages received from one of the two hoverboard control boards.
"""

import serial
import sys
import collections

device = sys.argv[1] # /dev/ttyUSB0
baudrate = 115200 #sys.argv[2]
logfile = sys.argv[2]

def lg(message, out):
    print(message)
    out.write(message)
    out.write('\n')

# given a byte number expressed in hex ASCII, find mod-256 8-bit checksum
def checksum(n):
    s = 0
    for i in n:
        s += i
    return [s % 256]

with open(logfile, 'w') as out:
    lg('Attempting to open serial connection...', out)
    with serial.Serial(sys.argv[1], 115200) as ser:
        lg(ser.__repr__(), out)
        lg('Serial connection opened successfully', out)

        deq = bytearray([0x00]*16)
        while True:
            deq = deq[1:] + deq[:1]
            deq[-1] = ser.read(1)[0]
            if checksum(deq[:-1]) == [deq[-1]] and deq[0] == 0xaa:
                lg(deq.hex(), out)
