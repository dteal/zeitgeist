#!/usr/bin/python3
"""
create_signals.py

This file creates several WAV files that can be used for FSK.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage as snd
import scipy.io.wavfile as siw

# define waveform parameters
fs = 44100 # (Hz) sample rate
fm = 256   # (samples/cycle) (~172 Hz) modulation frequency
f1 = 55    # (cycles/128 samples) (18949.2 Hz) first carrier frequency
f2 = 57    # (cycles/128 samples) (19638.3 Hz) second carrier frequency
sigma = 30 # (samples) width of gaussian filter on modulation
rpt = 51680# (number blocks) (~5 min) total output file length

# generate sample waveform
times = np.linspace(0, fm/fs, fm, False)
lowfreq = np.sin(2*np.pi*fs/fm*times)
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

def writefile(data, name):
    """
    Writes data array to wav file of given name.
    data is 1D numpy array of floats in [-1, 1].
    name is name of file.
    """
    data = (data*2147483647).astype(np.int32)
    data = np.concatenate([data]*rpt)
    siw.write(name, fs, data)

writefile(lowfreq, 'fsk_lowfreq.wav')
writefile(carrier1, 'fsk_f1.wav')
writefile(carrier2, 'fsk_f2.wav')
writefile(modulated1, 'fsk_f1_periodic.wav')
writefile(modulated2, 'fsk_f2_periodic.wav')
writefile(signal, 'fsk_complete.wav')
