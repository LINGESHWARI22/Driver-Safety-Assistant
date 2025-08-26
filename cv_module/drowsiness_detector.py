# cv_module/drowsiness_detector.py

# --- Suppress noisy TF/MediaPipe logs (must be first) ---
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from time import monotonic
import datetime

# Audio (safe fallback if default device not set)
try:
    import sounddevice as sd
    _AUDIO_OK = True
except Exception:
    _AUDIO_OK = False

# ----------------------------
# Settings (tune here)
# ----------------------------
# Hysteresis thresholds (use two thresholds to reduce flapping)
EAR_CLOSE_TH = 0.23   # go to DROWSY when smoothed EAR <= this
EAR_OPEN_TH  = 0.27   # return to AWAKE when smoothed EAR >= this

# Smoothing window (frames)
SMOOTH_N = 5          # moving average window

# Require eyes-closed for at least this long (seconds)
CLOSE_HOLD_SECS = 0.6

# Optional: draw eyes & EAR on frame
DRAW_LANDMARKS = True

# Logging
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "logs")
LOG_FILE = "alerts.log"

# ----------------------------
# MediaPipe init
# ----------------------------
mp_face_mesh = mp.solutions.face_mesh
# refine_landmarks=True gives more accurate eyes/iris points
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

# Eye landmarks (MediaPipe FaceMesh indices)
# Using a consistent 6-point set per eye for classic EAR:
RIGHT_EYE = [33, 160, 158, 133, 153, 144]   # p1,p2,p3,p4,p5,p6
LEFT_EYE  = [362, 385, 387, 263, 373, 380]  # p1,p2,p3,p4,p5,p6

# ----------------------------
# Utilities
# ----------------------------
def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)
    return os.path.join(LOG_DIR, LOG_FILE)

LOG_PATH = ensure_log_dir()

def log_state(state: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{ts} | {state}\n")

def play_beep():
    if not _AUDIO_OK:
        return
    try:
        fs = 44100
        duration = 0.45
        t = np.linspace(0, duration, int(fs * duration), False)
        wave = 0.4 * np.sin(2 * np.pi * 880 * t)  # 880 Hz, moderate volume
        sd.play(wave, fs, blocking=True)
    except Exception:
        # Don’t crash if audio device is unavailable
        pass

def eye_aspect_ratio(landmarks, eye_idx, w, h):
    # EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
    pts = [(landmarks.landmark[i].x * w, landmarks.landmark[i].y * h) for i in eye_idx]
    p1, p2, p3, p4, p5, p6 = [np.array(p) for p in pts]
    num = np.linalg.norm(p2 - p6) + np.linalg.norm(p3 - p5)
    den = 2.0 * np.linalg.norm(p1 - p4)
    if den == 0:
        return 0.0
    return float(num / den)

def draw_eye_points(frame, landmarks, eye_idx, color=(0, 255, 255)):
    h, w = frame.shape[:2]
    for i in eye_idx:
        x = int(landmarks.landmark[i].x * w)
        y = int(landmarks.landmark[i].y * h)
        cv2.circle(frame, (x, y), 2, color, -1)

# ----------------------------
# State machine
# ----------------------------
class DrowsinessFSM:
    def __init__(self):
        self.state = "AWAKE"          # or "DROWSY"
        self.close_start = None       # monotonic time when EAR first went below close threshold
        self.ear_hist = deque(maxlen=SMOOTH_N)

    def update(self, ear_value):
        # Smooth EAR
        self.ear_hist.append(ear_value)
        smooth_ear = sum(self.ear_hist) / len(self.ear_hist)

        now = monotonic()

        if self.state == "AWAKE":
            # detect potential close
            if smooth_ear <= EAR_CLOSE_TH:
                if self.close_start is None:
                    self.close_start = now
                elif (now - self.close_start) >= CLOSE_HOLD_SECS:
                    self.state = "DROWSY"
                    self.close_start = None
                    log_state("Drowsiness detected")
                    play_beep()
        else:  # DROWSY
            # only recover when clearly open (hysteresis)
            if smooth_ear >= EAR_OPEN_TH:
                self.state = "AWAKE"
                log_state("Eyes open")

        return smooth_ear, self.state

# ----------------------------
# Main
# ----------------------------
def run_drowsiness_detector():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # CAP_DSHOW helps on Windows
    if not cap.isOpened():
        print("ERROR: Cannot open camera.")
        return

    fsm = DrowsinessFSM()

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        # Improve stability: process a smaller image for speed, keep original for draw
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        ear_avg = None
        if results.multi_face_landmarks:
            face = results.multi_face_landmarks[0]

            # Compute EAR both eyes and average
            h, w = frame.shape[:2]
            ear_r = eye_aspect_ratio(face, RIGHT_EYE, w, h)
            ear_l = eye_aspect_ratio(face, LEFT_EYE,  w, h)
            ear_avg = (ear_r + ear_l) / 2.0

            # Update FSM
            smooth_ear, state = fsm.update(ear_avg)

            # Draw overlays
            if DRAW_LANDMARKS:
                draw_eye_points(frame, face, RIGHT_EYE, (0, 255, 255))
                draw_eye_points(frame, face, LEFT_EYE,  (0, 255, 255))

            # HUD
            cv2.putText(frame, f"EAR(raw): {ear_avg:.3f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame, f"EAR(smooth): {smooth_ear:.3f}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, f"State: {state}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

            if state == "DROWSY":
                cv2.putText(frame, "DROWSY ALERT!", (10, 140),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 3)

        else:
            # No face detected → reset pending close timer
            fsm.close_start = None
            cv2.putText(frame, "No face detected", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Drowsiness Detector", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

# ----------------------------
# Entry
# ----------------------------
if __name__ == "__main__":
    run_drowsiness_detector()
