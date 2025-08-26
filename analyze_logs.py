# analyze_logs.py
import os
import re
import pandas as pd
from datetime import datetime, timedelta

LOG_FILE = "data/logs/alerts.log"
OUT_FILE = "data/logs/episodes.csv"

# Max gap (in seconds) between consecutive drowsy alerts to still be the same episode
EPISODE_GAP_SECONDS = 5

if not os.path.exists(LOG_FILE):
    print("⚠️ No alerts.log found. Run the drowsiness detector first.")
    raise SystemExit

pattern = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*\|\s*(.+)$")

rows = []
with open(LOG_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        m = pattern.match(line)
        if not m:
            continue
        ts_str, state = m.groups()
        if state.strip() != "Drowsiness detected":
            continue
        try:
            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            rows.append(ts)
        except ValueError:
            # Skip anything that isn't a full timestamp
            continue

if not rows:
    print("✅ No drowsy alerts found in alerts.log (nothing to group).")
    # Write an empty CSV with headers so downstream scripts don't crash
    pd.DataFrame(columns=["start","end","duration_sec"]).to_csv(OUT_FILE, index=False)
    raise SystemExit

rows.sort()
episodes = []
start = rows[0]
end = rows[0]

for ts in rows[1:]:
    if (ts - end).total_seconds() <= EPISODE_GAP_SECONDS:
        # same episode, extend
        end = ts
    else:
        # close previous episode
        duration = max(1.0, (end - start).total_seconds())
        episodes.append({"start": start, "end": end, "duration_sec": duration})
        # start new
        start = ts
        end = ts

# append final episode
duration = max(1.0, (end - start).total_seconds())
episodes.append({"start": start, "end": end, "duration_sec": duration})

episodes_df = pd.DataFrame(episodes)
episodes_df["start"] = episodes_df["start"].dt.strftime("%Y-%m-%d %H:%M:%S")
episodes_df["end"] = episodes_df["end"].dt.strftime("%Y-%m-%d %H:%M:%S")

os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
episodes_df.to_csv(OUT_FILE, index=False)

print(f"✅ Episodes saved to {OUT_FILE}")
print(episodes_df.head())
