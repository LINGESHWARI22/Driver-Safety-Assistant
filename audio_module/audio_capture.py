import sounddevice as sd
import numpy as np

def play_alert():
    fs = 44100
    t = np.linspace(0, 0.2, int(fs*0.2), endpoint=False)
    tone = 0.5 * np.sin(2 * np.pi * 440 * t)
    sd.play(tone, fs)
    sd.wait()
