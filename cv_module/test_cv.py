import cv2
import mediapipe as mp
import numpy as np
import time

# Initialize mediapipe face mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

# EAR calculation function
def calculate_EAR(eye_landmarks, frame_w, frame_h):
    # Convert normalized landmarks to pixel coordinates
    points = [(int(lm.x * frame_w), int(lm.y * frame_h)) for lm in eye_landmarks]

    # EAR formula
    A = np.linalg.norm(np.array(points[1]) - np.array(points[5]))
    B = np.linalg.norm(np.array(points[2]) - np.array(points[4]))
    C = np.linalg.norm(np.array(points[0]) - np.array(points[3]))
    EAR = (A + B) / (2.0 * C)
    return EAR

# Open webcam
cap = cv2.VideoCapture(0)

# Thresholds
EAR_THRESHOLD = 0.25
CONSEC_FRAMES = 20  # how many frames to confirm drowsiness

counter = 0
drowsy = False

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame_h, frame_w = frame.shape[:2]
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Left & Right eye indices from Mediapipe
            left_eye_indices = [33, 160, 158, 133, 153, 144]   # [p1, p2, p3, p4, p5, p6]
            right_eye_indices = [362, 385, 387, 263, 373, 380]

            # Extract landmarks
            left_eye = [face_landmarks.landmark[i] for i in left_eye_indices]
            right_eye = [face_landmarks.landmark[i] for i in right_eye_indices]

            # Calculate EAR
            left_EAR = calculate_EAR(left_eye, frame_w, frame_h)
            right_EAR = calculate_EAR(right_eye, frame_w, frame_h)
            EAR = (left_EAR + right_EAR) / 2.0

            # Draw eyes
            for lm in left_eye + right_eye:
                x, y = int(lm.x * frame_w), int(lm.y * frame_h)
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            # Drowsiness detection
            if EAR < EAR_THRESHOLD:
                counter += 1
                if counter >= CONSEC_FRAMES:
                    drowsy = True
                    cv2.putText(frame, "DROWSY ALERT!", (100, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            else:
                counter = 0
                drowsy = False

            # Show EAR on screen
            cv2.putText(frame, f"EAR: {EAR:.2f}", (30, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow('Drowsiness Detector', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
