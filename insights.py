import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os

# Make sure reports folder exists
os.makedirs("reports", exist_ok=True)

# Load episodes.csv
episodes_path = "data/logs/episodes.csv"

# --- Safety check ---
if not os.path.exists(episodes_path) or os.path.getsize(episodes_path) == 0:
    print("⚠️ episodes.csv is missing or empty. Run analyze_logs.py first.")
    exit()

try:
    df = pd.read_csv(episodes_path)
except pd.errors.EmptyDataError:
    print("⚠️ episodes.csv is empty or corrupted. Run analyze_logs.py again.")
    exit()

if df.empty:
    print("⚠️ No data found in episodes.csv")
    exit()

# Convert timestamps to datetime (only works for proper YYYY-MM-DD HH:MM:SS)
df["start"] = pd.to_datetime(df["start"], errors="coerce")
df["end"] = pd.to_datetime(df["end"], errors="coerce")

# Compute duration in seconds
df["duration_sec"] = (df["end"] - df["start"]).dt.total_seconds()

# Drop invalid rows (like mm:ss ones that can’t convert)
df = df.dropna(subset=["start", "end", "duration_sec"])

# ---------------------- SUMMARY ----------------------
total_episodes = len(df)
avg_duration = df["duration_sec"].mean() if total_episodes > 0 else 0
longest_episode = df["duration_sec"].max() if total_episodes > 0 else 0
most_drowsy_day = (
    df["start"].dt.date.value_counts().idxmax() if total_episodes > 0 else "N/A"
)

print("\n📊 Episode Summary:")
print(f"✅ Total Episodes: {total_episodes}")
print(f"⏱️ Average Duration: {avg_duration:.2f} sec" if total_episodes > 0 else "No valid data")
print(f"⏰ Longest Episode: {longest_episode:.2f} sec" if total_episodes > 0 else "")
print(f"📅 Most Drowsy Day: {most_drowsy_day}" if total_episodes > 0 else "")

# ---------------------- VISUALS ----------------------
if total_episodes > 0:
    # Daily episode counts
    daily_counts = df.groupby(df["start"].dt.date).size()

    plt.figure(figsize=(8, 4))
    daily_counts.plot(kind="bar")
    plt.title("Daily Drowsy Episodes")
    plt.ylabel("Count")
    plt.savefig("reports/daily_trend.png")
    plt.close()

    # Histogram of durations
    plt.figure(figsize=(8, 4))
    df["duration_sec"].plot(kind="hist", bins=10)
    plt.title("Distribution of Episode Durations (sec)")
    plt.xlabel("Duration (sec)")
    plt.savefig("reports/duration_hist.png")
    plt.close()

    # Interactive dashboard
    fig = px.bar(daily_counts, title="Daily Drowsy Episodes")
    fig.write_html("reports/dashboard.html")

    print("\n📂 Reports generated in 'reports' folder:")
    print("   - daily_trend.png")
    print("   - duration_hist.png")
    print("   - dashboard.html")
else:
    print("\n⚠️ No valid episodes to analyze. Check episodes.csv")
