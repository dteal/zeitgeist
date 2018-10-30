#!/usr/bin/python3
"""
receiver.py

This file tracks an acoustic FSK signal by the phase difference between two microphones.
"""

import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd

# define waveform parameters
fs = 44100 # (Hz) sample rate
fm = 256   # (samples/cycle) (~172 Hz) modulation frequency
f1 = 55    # (cycles/128 samples) (18949.2 Hz) first carrier frequency
f2 = 57    # (cycles/128 samples) (19638.3 Hz) second carrier frequency

# generate sample waveform
"""
times = np.linspace(0, fm/fs, fm, False)
carrier1 = np.sin(2*np.pi*fs*2/fm*f1*times)
carrier2 = np.sin(2*np.pi*fs*2/fm*f2*times)
blank = times*0
signal = np.concatenate((carrier1[:int(fm/2)], carrier2[int(fm/2):]))
"""

# define helper functions
def corr(a, b):
    """
    Correlates a and b cyclically.
    a is a NxM numpy array --- data for M channels.
    b is a Nx1 numpy array.
    Returns an NxM array.
    """
    output = np.zeros(a.shape)
    for i in range(a.shape[0]):
        output[i] = np.sum(a*np.roll(b, i, axis=0), axis=0)
    return output

def avg(a, n):
    """takes cyclic running average of a with 2n-1 points"""
    output = np.zeros((len(a)))
    for i in range(len(a)):
        temp = np.roll(a, -i)
        output[i] = (temp[0]+np.sum(temp[1:n+1])+np.sum(temp[len(a)-n:]))/(2*n+1)
    return output

def callback(data, frames, time, status):
    print(data.shape)

a = np.array([[1,1], [2,0], [3,0]])
b = np.array([[1],[0],[0]])

print(a.shape)
print(corr(a,b))

"""
stream = sd.InputStream(channels=1, samplerate=fs, callback=callback, blocksize=fm)
with stream:
    while True:
        pass
"""

"""
# split signal in two, simulate noise by messing up signal
np.random.seed(1)
signal_left = signal[:]# + np.random.normal(0, 1, fm)
signal_left = signal_left + 10*np.sin(2*np.pi*400*times)

signal_right = signal[:]# + np.random.normal(0, 1, fm)
signal_right = signal_right + 10*np.sin(2*np.pi*200*times)
signal_right = signal_right*0.5
signal_right = np.roll(signal_right, int(-50))

# read signal
def read(s):
    mask1 = np.concatenate((carrier1[:int(fm/2)], blank[int(fm/2):]))
    mask2 = np.concatenate((carrier2[:int(fm/2)], blank[int(fm/2):]))
    corr1 = np.abs(corr(s, mask1))
    corr2 = np.abs(corr(s, mask2))
    return avg(corr1-corr2, int(fm/4))

read_left = read(signal_left)
read_right = read(signal_right)

# compare signals to determine phase difference
comp = corr(read_left, read_right)
diff = comp.argmax()
dist = diff
if diff > fm/2:
    dist = diff-fm

"""

