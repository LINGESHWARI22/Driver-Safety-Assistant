Driver Safety Assistant

An AI-powered Driver Monitoring System that detects driver drowsiness, plays beep alerts, and generates intelligent summaries of driving behavior using LLMs.
This project combines Computer Vision, Audio Processing, and Natural Language Processing to make driving safer.

✨ Features

👀 Eye Blink & Drowsiness Detection (using EAR – Eye Aspect Ratio)

🔔 Beep Alerts when drowsiness is detected

🎙️ Audio Recording & Playback for testing alerts

📝 Log System that records all alerts with timestamps

🤖 LLM-powered Driving Summary that provides a quick overview of driver behavior

📊 Visualization of detection results in real-time

🛠️ Tech Stack

Languages & Frameworks:

Python 🐍
Computer Vision (CV):
OpenCV
Mediapipe
dlib
Audio Processing:
PyAudio
sounddevice
Machine Learning / NLP:
Hugging Face Transformers (BART for summarization)
TensorFlow Lite
Others:
Numpy, OS, Logging

📂 Project Structure

DriverSafetyAssistant/
│
├── cv_module/               # Computer Vision for eye & drowsiness detection
│   └── drowsiness_detector.py
│
├── audio_module/            # Beep alert & audio recording
│   └── test_audio.py
│
├── llm_module/              # AI summarizer for driving logs
│   └── alert_generator.py
│
├── data/
│   └── logs/alerts.log      # Log file for storing drowsy events
│
├── requirements.txt         # Dependencies
└── README.md                # Documentation


▶️ How to Run
1️⃣ Run the Drowsiness Detector (CV Module)
python -m cv_module.drowsiness_detector


This opens a webcam feed and displays:
EAR(raw)
EAR(smooth)
Driver State (DROWSY or ALERT)
A big DROWSY ALERT! in red if drowsiness is detected

2️⃣ Test Audio Beep & Recording
python -m audio_module.test_audio

Sample output:
🔔 Playing beep...
🎙️ Recording for 5 seconds...
✅ Recording complete. Playing back...
✅ Playback finished

3️⃣ Generate LLM-based Driving Summary
python -m llm_module.alert_generator

Sample output:
📋 Driving Summary
--------------------
Driver was mostly attentive but showed signs of drowsiness 
between 02:07 and 02:12. Multiple eye-closure events detected. 
Beep alerts were triggered successfully.
