import winsound

def play_beep():
    frequency = 1000  # Hz
    duration = 500    # ms
    winsound.Beep(frequency, duration)
