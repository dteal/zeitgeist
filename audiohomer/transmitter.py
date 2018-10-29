#!/usr/bin/python3

import sounddevice as sd
import numpy as np


# define waveform parameters
fs = 44100 # (Hz) sample rate
fm = 256   # (samples/cycle) (~172 Hz) modulation frequency
f1 = 55    # (cycles/128 samples) (18949.2 Hz) first carrier frequency
f2 = 57    # (cycles/128 samples) (19638.3 Hz) second carrier frequency

# generate sample waveform
times = np.linspace(0, fm/fs, fm, False)
#carrier1 = np.sin(2*np.pi*fs*2/fm*f1*times)
#carrier2 = np.sin(2*np.pi*fs*2/fm*f2*times)
blank = times*0
#signal = np.concatenate((carrier1[:int(fm/2)], carrier2[int(fm/2):]))
signal = np.sin(2*np.pi*fs*2/fm*times)
np.reshape(signal, (len(signal),1))

def callback(outdata, frames, time, status):
    assert(frames == fm)
    outdata[:] = signal

with sd.OutputStream(samplerate=fs, channels=1, callback=callback, blocksize=fm):
    while True:
        pass