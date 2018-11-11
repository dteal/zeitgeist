#!/usr/bin/python3
"""
This program inserts itself in between the two hoverboard control boards, each of which is connected to the program-running computer by a USB-serial converter. Commands sent from one board to another may be changed.
"""

import serial
import sys
import collections


master = '/dev/ttyUSB1'
slave = '/dev/ttyUSB0'
baudrate = 115200 #sys.argv[2]
logfile = sys.argv[1]

def lg(message, out):
    print(message)
    out.write(message)
    out.write('\n')

def checksum(code):
    """Given a byte number expressed in hex ASCII, find mod-256 8-bit checksum."""
    return sum(code) % 256

with open(logfile, 'w') as out:
    lg('Attempting to open serial connection 1...', out)
    with serial.Serial(master, 115200) as ser1:
        lg(ser1.__repr__(), out)
        lg('Serial connection 1 opened successfully.', out)
        lg('Attempting to open serial connection 2...', out)
        with serial.Serial(slave, 115200) as ser2:
            lg(ser2.__repr__(), out)
            lg('Serial connection 2 opened successfully.', out)
 
            deq1 = bytearray([0x00]*16)
            ldeq1 = deq1[:]
            deq2 = bytearray([0x00]*16)
            ldeq2 = deq2[:]
            while True:
                if ser1.in_waiting:
                    deq1 = deq1[1:] + deq1[:1]
                    deq1[-1] = ser1.read(1)[0]
                    if checksum(deq1[:-1]) == deq1[-1] and deq1[0] == 0xaa:
                        # modify signal
                        ldeq1 = deq1[:]
                        lg(ldeq1.hex() + ' ' + ldeq2.hex(), out)
                        ser2.write(deq1)
                if ser2.in_waiting:
                    deq2 = deq2[1:] + deq2[:1]
                    deq2[-1] = ser2.read(1)[0]
                    if checksum(deq2[:-1]) == deq2[-1] and deq2[0] == 0xaa:

                        ldeq2 = deq2[:]
                        lg(ldeq1.hex() + ' ' + ldeq2.hex(), out)
                        ser1.write(deq2)
