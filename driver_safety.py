import cv2
import mediapipe as mp
import numpy as np
import sounddevice as sd
import logging
import csv
from datetime import datetime
from pathlib import Path

# -----------------------------
# Setup
# -----------------------------
logging.basicConfig(
    filename="data/logs/alerts.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

data_dir = Path("data/logs/snaps")
data_dir.mkdir(parents=True, exist_ok=True)

episodes_file = Path("data/logs/episodes.csv")
if not episodes_file.exists():
    with open(episodes_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["start", "end", "event"])

# Mediapipe setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# Thresholds
EAR_THRESHOLD = 0.22       # Eye Aspect Ratio
EAR_CONSEC_FRAMES = 10     # Frames to trigger drowsiness
MAR_THRESHOLD = 0.5        # Mouth Aspect Ratio for yawns

# State variables
COUNTER = 0
drowsy_status = False
drowsy_start = None
yawn_status = False
yawn_start = None

# -----------------------------
# Helper functions
# -----------------------------
def play_alert():
    fs = 44100
    t = np.linspace(0, 0.2, int(fs * 0.2), endpoint=False)
    tone = 0.5 * np.sin(2 * np.pi * 440 * t)
    sd.play(tone, fs)
    sd.wait()

def euclidean_distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def eye_aspect_ratio(landmarks, eye_indices):
    p1, p2, p3, p4, p5, p6 = [landmarks[i] for i in eye_indices]
    A = euclidean_distance(p2, p6)
    B = euclidean_distance(p3, p5)
    C = euclidean_distance(p1, p4)
    return (A + B) / (2.0 * C)

def mouth_aspect_ratio(landmarks, mouth_indices):
    top_lip = landmarks[mouth_indices[13]]
    bottom_lip = landmarks[mouth_indices[14]]
    left = landmarks[mouth_indices[78]]
    right = landmarks[mouth_indices[308]]
    vertical = euclidean_distance(top_lip, bottom_lip)
    horizontal = euclidean_distance(left, right)
    return vertical / horizontal

def save_snapshot(frame, event_type):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{event_type}_{ts}.png"
    out = data_dir / filename
    if frame is not None:
        cv2.imwrite(str(out), frame)
        return out.name
    return None

# -----------------------------
# Main loop
# -----------------------------
cap = cv2.VideoCapture(0)
print("🚗 Driver Safety System Running... Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w, _ = frame.shape
            landmarks = [(int(pt.x * w), int(pt.y * h)) for pt in face_landmarks.landmark]

            # EAR calculation (eyes)
            left_eye_indices = [33, 160, 158, 133, 153, 144]
            right_eye_indices = [362, 385, 387, 263, 373, 380]
            leftEAR = eye_aspect_ratio(landmarks, left_eye_indices)
            rightEAR = eye_aspect_ratio(landmarks, right_eye_indices)
            ear = (leftEAR + rightEAR) / 2.0

            # MAR calculation (mouth)
            mouth_indices = list(range(0, 468))
            mar = mouth_aspect_ratio(landmarks, mouth_indices)

            # -----------------
            # Debug prints
            # -----------------
            print(f"EAR: {ear:.3f} | MAR: {mar:.3f} | COUNTER: {COUNTER}")

            # -----------------
            # Drowsiness detection
            # -----------------
            if ear < EAR_THRESHOLD:
                COUNTER += 1
                if COUNTER >= EAR_CONSEC_FRAMES and not drowsy_status:
                    drowsy_status = True
                    drowsy_start = datetime.now()
                    logging.info("Drowsiness detected")
                    snap = save_snapshot(frame, "drowsy")
                    if snap:
                        logging.info(f"Snapshot saved: {snap}")
                    play_alert()  # Beep alert
            else:
                if drowsy_status:
                    drowsy_status = False
                    drowsy_end = datetime.now()
                    logging.info("Eyes open")
                    with open(episodes_file, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([drowsy_start, drowsy_end, "drowsy"])
                COUNTER = 0

            # -----------------
            # Yawning detection
            # -----------------
            if mar > MAR_THRESHOLD and not yawn_status:
                yawn_status = True
                yawn_start = datetime.now()
                logging.info("Yawning detected")
                snap = save_snapshot(frame, "yawn")
                if snap:
                    logging.info(f"Snapshot saved: {snap}")
                play_alert()  # Beep alert for yawn

            elif mar <= MAR_THRESHOLD and yawn_status:
                yawn_status = False
                yawn_end = datetime.now()
                logging.info("Yawn ended")
                with open(episodes_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([yawn_start, yawn_end, "yawn"])

    cv2.imshow("Driver Safety", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
