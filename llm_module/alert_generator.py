import os
from transformers import pipeline

# Initialize summarization model (can change model if needed)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def generate_alert_summary(log_file="data/logs/alerts.log"):
    """Read alerts log and summarize driver behavior"""
    if not os.path.exists(log_file):
        return "⚠️ No logs found yet."

    with open(log_file, "r", encoding="utf-8") as f:
        logs = f.read()

    if not logs.strip():
        return "⚠️ Log file is empty."

    # Keep only the recent logs to avoid model overload
    logs = logs[-2000:]  

    # Generate summary
    summary = summarizer(
        logs, max_length=120, min_length=30, do_sample=False
    )

    return summary[0]["summary_text"]


# ------------------ MAIN EXECUTION ------------------
if __name__ == "__main__":
    result = generate_alert_summary()
    print("📋 Driving Summary")
    print("--------------------")
    print(result)
