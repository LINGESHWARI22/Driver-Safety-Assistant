import numpy as np
import simpleaudio as sa
import sounddevice as sd
import soundfile as sf

def play_beep(duration=0.5, freq=1000):
    print("🔔 Playing beep...")   # Debug print
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(freq * t * 2 * np.pi) * 0.3
    audio = (tone * 32767).astype(np.int16)
    play_obj = sa.play_buffer(audio, 1, 2, sample_rate)
    play_obj.wait_done()

def record_and_playback(duration=5, filename="data/test_record.wav"):
    print("🎙️ Recording for 5 seconds...")
    rec = sd.rec(int(duration * 44100), samplerate=44100, channels=1)
    sd.wait()
    sf.write(filename, rec, 44100)
    print("✅ Recording complete. Playing back...")

    data, fs = sf.read(filename, dtype='float32')
    sd.play(data, fs)
    sd.wait()
    print("✅ Playback finished")

if __name__ == "__main__":
    # First play a test beep
    play_beep()
    # Then test mic
    record_and_playback()
