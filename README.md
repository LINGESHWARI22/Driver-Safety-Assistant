# 🚗 Driver Safety Assistant  
**Real-time Drowsiness Detection with Computer Vision, Audio Alerts & LLM Insights**

An AI-powered driver monitoring system that detects drowsiness from facial landmarks (eyes & mouth), plays instant beep alerts, logs events, and generates intelligent summaries of driving behavior using LLMs. Built for reliability and easy local use.

## ✨ Features
- **👀 Eye Blink & Drowsiness Detection**  
  EAR (Eye Aspect Ratio) + smoothing → stable DROWSY/AWAKE states.
- **🔔 Instant Beep Alerts**  
  Loud, OS-native beep when drowsiness persists.
- **📝 Structured Logging**  
  Every state change recorded with timestamps (`data/logs/alerts.log`).
- **🤖 LLM Summaries (Optional)**  
  Summarizes logs into a human-readable driving report.
- **📊 On-Screen Overlay**  
  Live EAR values, state text, and bold **DROWSY ALERT!** on the webcam feed.
- **🎙️ Audio Test Utility**  
  Record & playback to verify audio pipeline.

---

## 🛠 Tech Stack (by function)
**Computer Vision**
- Python, OpenCV
- MediaPipe Face Mesh (lightweight facial landmarks)
- NumPy
**Audio**
- Windows `winsound` (beep)
- (Utility) sounddevice / wave for quick record/playback
**LLM / NLP (Optional)**
- Hugging Face Transformers (e.g., `facebook/bart-large-cnn`) for log summaries
**Utilities**
- Logging, CSV/Files
- (Optional) TensorFlow Lite note: used by MediaPipe under the hood for fast landmark inference

▶️ How to Run 1️⃣ Run the Drowsiness Detector (CV Module) python -m cv_module.drowsiness_detector

This opens a webcam feed and displays: EAR(raw) EAR(smooth) Driver State (DROWSY or ALERT) A big DROWSY ALERT! in red if drowsiness is detected

2️⃣ Test Audio Beep & Recording python -m audio_module.test_audio

Sample output: 🔔 Playing beep... 🎙️ Recording for 5 seconds... ✅ Recording complete. Playing back... ✅ Playback finished

3️⃣ Generate LLM-based Driving Summary python -m llm_module.alert_generator

Sample output: 📋 Driving Summary
Driver was mostly attentive but showed signs of drowsiness between 02:07 and 02:12. Multiple eye-closure events detected. Beep alerts were triggered successfully. i want step by step tech stacjk and features and also title should be attractive iand little big
ChatGPT said:
Thought for 11s

Here’s a polished, copy-paste-ready README.md you can use. It’s short where it should be, clear, and looks great on GitHub.

# 🚗 Driver Safety Assistant  
**Real-time Drowsiness Detection with Computer Vision, Audio Alerts & LLM Insights**

An AI-powered driver monitoring system that detects drowsiness from facial landmarks (eyes & mouth), plays instant beep alerts, logs events, and generates intelligent summaries of driving behavior using LLMs. Built for reliability and easy local use.

---

## ✨ Features

- **👀 Eye Blink & Drowsiness Detection**  
  EAR (Eye Aspect Ratio) + smoothing → stable DROWSY/AWAKE states.
- **🔔 Instant Beep Alerts**  
  Loud, OS-native beep when drowsiness persists.
- **📝 Structured Logging**  
  Every state change recorded with timestamps (`data/logs/alerts.log`).
- **🤖 LLM Summaries (Optional)**  
  Summarizes logs into a human-readable driving report.
- **📊 On-Screen Overlay**  
  Live EAR values, state text, and bold **DROWSY ALERT!** on the webcam feed.
- **🎙️ Audio Test Utility**  
  Record & playback to verify audio pipeline.

---

## 🛠 Tech Stack (by function)

**Computer Vision**
- Python, OpenCV
- MediaPipe Face Mesh (lightweight facial landmarks)
- NumPy

**Audio**
- Windows `winsound` (beep)
- (Utility) sounddevice / wave for quick record/playback

**LLM / NLP (Optional)**
- Hugging Face Transformers (e.g., `facebook/bart-large-cnn`) for log summaries

**Utilities**
- Logging, CSV/Files
- (Optional) TensorFlow Lite note: used by MediaPipe under the hood for fast landmark inference

---

## 📂 Project Structure



DriverSafetyAssistant/
├── cv_module/ # Computer vision
│ ├── drowsiness_detector.py
│ └── face_landmark_utils.py
├── audio_module/ # Beep + audio tests
│ ├── audio_alert.py
│ └── test_audio.py
├── llm_module/ # LLM summaries from logs (optional)
│ ├── alert_generator.py
│ └── test_llm.py
├── data/
│ └── logs/
│ └── alerts.log # Drowsiness/awake events
├── main.py # Thin launcher (optional)
├── requirements.txt
└── README.md


> **Tip:** We keep `data/logs/.gitkeep` so the folder exists, but the actual logs are ignored by Git.

---

## ▶️ Quick Start

### 1) Setup (once)

# from project root
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
2) Run the Drowsiness Detector (opens webcam)
python -m cv_module.drowsiness_detector

What you’ll see on the video:
EAR(raw) and EAR(smooth) values
State: AWAKE or State: DROWSY
Big red DROWSY ALERT! when triggered
Beep sound during drowsy events

3) Test Audio Beep & Recording (utility)
python -m audio_module.test_audio
Expected:
🔔 Playing beep...
🎙️ Recording for 5 seconds...
✅ Recording complete. Playing back...
✅ Playback finished

4) Generate AI Summary (optional, uses LLM)
python -m llm_module.alert_generator

