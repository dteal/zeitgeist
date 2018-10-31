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
fm = 25   # (Hz) baud rate
fh = 19000 # (Hz) carrier frequency
length = 5 # (min) desired output length

# generate modulated signal
times = np.linspace(0, length*60, int(44100*length*60), endpoint=False)
# generate carrier signal
carrier = np.sin(2*np.pi*times*fh)
# generate envelope signal
modulator = np.sin(2*np.pi*times*fm)
# create modulated signal
signal = carrier*modulator

def writefile(data, name):
    """
    Writes data array to wav file of given name.
    data is 1D numpy array of floats in [-1, 1].
    name is name of file.
    """
    data = (data*2147483647).astype(np.int32)
    siw.write(name, fs, data)

writefile(signal, 'sine.wav')
