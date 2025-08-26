# main.py
import cv2
from cv_module.face_landmark_utils import eye_aspect_ratio, mouth_aspect_ratio
from audio_module.audio_alert import play_beep
from llm_module.alert_generator import generate_alert

# Thresholds
EYE_AR_THRESH = 0.25
MOUTH_AR_THRESH = 0.7
CONSEC_FRAMES = 15

def drowsiness_monitor():
    print("🚗 Starting Driver Safety Assistant with AI alerts...")

    cap = cv2.VideoCapture(0)  # Webcam
    frame_counter = 0
    alert_text = ""

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # EAR & MAR (dummy for now – replace with real values later)
        ear = eye_aspect_ratio()
        mar = mouth_aspect_ratio()

        # Check drowsiness
        if ear < EYE_AR_THRESH or mar > MOUTH_AR_THRESH:
            frame_counter += 1
            if frame_counter >= CONSEC_FRAMES:
                # 🔹 Generate LLM-based alert instead of static text
                alert_text = generate_alert("Drowsiness detected. Suggest safe advice.")
                play_beep()
        else:
            frame_counter = 0
            alert_text = ""

        # Overlay alert on video
        if alert_text:
            cv2.putText(frame, alert_text, (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Driver Safety Assistant", frame)

        # Quit with 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    drowsiness_monitor()
