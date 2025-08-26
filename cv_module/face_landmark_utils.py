# cv_module/face_landmark_utils.py

import random

def eye_aspect_ratio(landmarks=None, eye_indices=None):
    """
    Dummy EAR function
    Replace with actual dlib/mediapipe implementation later.
    """
    return random.uniform(0.2, 0.4)  # simulate blinking/drowsiness

def mouth_aspect_ratio(landmarks=None, mouth_indices=None):
    """
    Dummy MAR function
    Replace with actual dlib/mediapipe implementation later.
    """
    return random.uniform(0.5, 0.8)  # simulate yawning
