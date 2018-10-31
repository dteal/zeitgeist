#!/usr/bin/python3
"""
simulation.py

This file runs a simulation of receiving a two-tone FSK signal used for acoustic direction tracking.
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage as snd

# define waveform parameters
fs = 44100 # (Hz) sample rate
fm = 256   # (samples/cycle) (~172 Hz) modulation frequency
f1 = 55    # (cycles/128 samples) (18949.2 Hz) first carrier frequency
f2 = 57    # (cycles/128 samples) (19638.3 Hz) second carrier frequency
sigma = 64 # (samples) width of gaussian filter on modulation

# generate sample waveform
times = np.linspace(0, fm/fs, fm, False)
carrier1 = np.sin(2*np.pi*fs*2/fm*f1*times)
carrier2 = np.sin(2*np.pi*fs*2/fm*f2*times)
constant = times*0+1
blank = times*0
modulator = np.concatenate((blank[:int(fm/4)], constant[int(fm/4):int(3*fm/4)], blank[int(3*fm/4):]))
modulator = snd.gaussian_filter(modulator, sigma=sigma)
modulator1 = np.roll(modulator, int(-fm/4))
modulator2 = np.roll(modulator, int(fm/4))
modulated1 = carrier1 * modulator1
modulated2 = carrier2 * modulator2
signal = modulated1 + modulated2

if True:
    plt.plot(times, signal)
    plt.title('Transmitted Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.show()

# define helper functions
def corr(a, b):
    """correlates a and b cyclically"""
    assert(len(a)==len(b))
    output = np.zeros((len(a)))
    for i in range(len(a)):
        output[i] = np.sum(a*np.roll(b, i))
    return output
def avg(a, n):
    """takes cyclic running average of a with 2n-1 points"""
    output = np.zeros((len(a)))
    for i in range(len(a)):
        temp = np.roll(a, -i)
        output[i] = (temp[0]+np.sum(temp[1:n+1])+np.sum(temp[len(a)-n:]))/(2*n+1)
    return output

# split signal in two, simulate noise by messing up signal
np.random.seed(1)
signal_left = signal[:]# + np.random.normal(0, 1, fm)
signal_left = signal_left + 10*np.sin(2*np.pi*400*times)

signal_right = signal[:]# + np.random.normal(0, 1, fm)
signal_right = signal_right + 10*np.sin(2*np.pi*200*times)
signal_right = signal_right*0.5
signal_right = np.roll(signal_right, int(-50))

if True:
    plt.plot(times, signal_left, label='left')
    plt.plot(times, signal_right, label='right')
    plt.title('Received Signals')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()

# read signal
def read(s):
    mask1 = np.concatenate((carrier1[:int(fm/2)], blank[int(fm/2):]))
    mask2 = np.concatenate((carrier2[:int(fm/2)], blank[int(fm/2):]))
    corr1 = np.abs(corr(s, mask1))
    corr2 = np.abs(corr(s, mask2))
    return avg(corr1-corr2, int(fm/4))

read_left = read(signal_left)
read_right = read(signal_right)
if True:
    plt.plot(times, read_left, label='left')
    plt.plot(times, read_right, label='right')
    plt.title('Read Signals')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()

# compare signals to determine phase difference
comp = corr(read_left, read_right)
diff = comp.argmax()
dist = diff
if diff > fm/2:
    dist = diff-fm
if True:
    plt.axvline(x=times[diff], color='gray')
    plt.axvline(x=times[0], color='gray')
    plt.axvline(x=times[-1], color='gray')
    plt.plot(times, comp)
    plt.plot(times[diff], comp[diff], 'o', color='orange')
    plt.title('Signal Phase Difference of {}'.format(dist))
    plt.xlabel('Time (s)')
    plt.ylabel('Right/Left Correlation')
    plt.show()


