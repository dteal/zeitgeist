#!/usr/bin/python3
"""
create_signals.py

This file creates several WAV files that can be used for FSK.

Thanks to https://natronics.github.io/blag/2014/gps-prn/
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage as snd
import scipy.io.wavfile as siw

# define waveform parameters
fs = 44100 # (Hz) sample rate
fm = 100   # (Hz) baud rate
fh = 19000 # (Hz) carrier frequency
length = 5 # (min) desired output length

class Generator:
    """Generate gold code (a la GPS PRN)"""
    def __init__(self):
        self.c1 = np.ones((10))
        self.c2 = np.ones((10))
    def shift(self):
        c1 = self.c1
        c2 = self.c2
        # get output
        out1 = c1[9]
        out2 = (c2[1]+c2[5]) % 2
        # shift registers
        self.c1 = np.roll(c1, 1)
        self.c2 = np.roll(c2, 1)
        self.c1[0] = (c1[9]+c1[2]) % 2
        self.c2[0] = (c2[1]+c2[2]+c2[5]+c2[7]+c2[8]+c2[9]) % 2
        # finish
        return (out1+out2) % 2
    def get_code(self):
        code = np.zeros((1023))
        for i in range(1023):
            code[i] = self.shift()
        return code

# generate code
g = Generator()
code = g.get_code()

# generate modulated signal
times = np.linspace(0, code.shape[0]/fm, int(44100*code.shape[0]/fm), endpoint=False)
# generate carrier signal
carrier = np.sin(2*np.pi*times*fh)
# generate envelope for single bit
blank = times*0
constant = blank+1
envelope_bit = np.concatenate((constant[:int(fs/fm)], blank[int(fs/fm):]))
envelope_bit = np.roll(envelope_bit, int(fs/fm))
envelope_bit = snd.gaussian_filter(envelope_bit, sigma=5)
envelope_bit = np.roll(envelope_bit, int(-fs/fm))
# create modulated signal
signal = blank[:]
for i in range(code.shape[0]):
    signal = signal + code[i]*np.roll(envelope_bit,int(i*fs/fm))*carrier

repeats = int(length * 60 * fm / code.shape[0])

def writefile(data, name):
    """
    Writes data array to wav file of given name.
    data is 1D numpy array of floats in [-1, 1].
    name is name of file.
    """
    data = (data*2147483647).astype(np.int32)
    siw.write(name, fs, data)

writefile(np.concatenate([signal]*repeats), 'goldcode.wav')
