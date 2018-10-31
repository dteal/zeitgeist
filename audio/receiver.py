#!/usr/bin/python3
"""
receiver.py

This file tracks an acoustic FSK signal by the phase difference between two microphones.
"""

import time
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import scipy.signal as sp

# define waveform parameters
fs = 44100 # (Hz) sample rate
fm = 256   # (samples/cycle) (~172 Hz) modulation frequency
f1 = 55    # (cycles/128 samples) (18949.2 Hz) first carrier frequency
f2 = 57    # (cycles/128 samples) (19638.3 Hz) second carrier frequency

# generate sample waveform
times = np.linspace(0, fm/fs, fm, False)
carrier1 = np.sin(2*np.pi*fs*2/fm*f1*times)
carrier2 = np.sin(2*np.pi*fs*2/fm*f2*times)
blank = times*0
mask1 = np.reshape(np.concatenate((carrier1[:int(fm/2)], blank[int(fm/2):])), (fm))
mask2 = np.reshape(np.concatenate((carrier2[:int(fm/2)], blank[int(fm/2):])), (fm))

# define helper functions
def corr2(a, b):
    """
    Correlates a and b cyclically.
    a is a NxM numpy array --- data for M channels.
    b is a Nx1 numpy array.
    Returns an NxM array.
    """
    output = np.zeros(a.shape)
    for i in range(a.shape[0]):
        output[i] = np.sum(np.abs(a*np.roll(b, i, axis=0)), axis=0)
    return output

def corr(a, b):
    """correlates a and b cyclically"""
    assert(len(a)==len(b))
    output = np.zeros((len(a)))
    plt.plot(a); plt.show()
    for i in range(len(a)):
        output[i] = np.sum(np.abs(a*np.roll(b, i)))
    plt.plot(output); plt.show()
    return output

def avg(a, n):
    """
    Takes cyclic running average of a with 2n-1 points.
    a is a NxM numpy array --- data for M channels.
    Returns an NxM array.
    """
    output = np.zeros(a.shape)
    for i in range(a.shape[0]):
        temp = np.roll(a, -i, axis=0)
        output[i] = (temp[0,:]+np.sum(temp[1:n+1,:], axis=0)+np.sum(temp[a.shape[0]-n:,:], axis=0))/(2*n+1)
    return output


average = np.zeros((50))
count = 0

while True:

    data = sd.rec(fm*10, samplerate=fs, channels=2)
    plt.plot(data, label='original')

    b, a = sp.butter(3, 0.5, btype='high')
    data2 = sp.filtfilt(b, a, data, padlen=50, axis=0)
    plt.plot(data2, label='filter')

    data3 = np.abs(data2)
    plt.plot(data3, label='abs')

    n = 5
    data4 = np.zeros(data3.shape)
    for i in range(data3.shape[0]):
        temp = np.roll(data3, -i, axis=0)
        data4[i] = (temp[0]+np.sum(temp[1:n+1], axis=0)+np.sum(temp[data3.shape[0]-n:], axis=0))/(2*n+1)
    plt.plot(data4, label='avg')

    b, a = sp.butter(3, 0.01, btype='low')
    data5 = sp.filtfilt(b, a, data4, padlen=50, axis=0)*10
    plt.plot(data5, label='filter2')

    data6 = np.zeros(data5.shape[0])
    for i in range(data5.shape[0]):
        data6[i] = np.sum(data5[:,0]*np.roll(data5[:,1], i))/1000
    plt.plot(data6[256:512], label='output')

    diff = data6[:256].argmax()
    dist = diff
    if diff > 256/2:
        dist = diff-256

    plt.title('{}'.format(dist))

    print(dist)

    plt.legend()
    plt.show()

