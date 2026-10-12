# -*- coding: utf-8 -*-
"""Retry failed subtitle downloads + find missing Immortals video."""
import json, os, subprocess, time, re

BASE = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q006-移动中瞄准定位\YouTube原始数据"
IN = os.path.join(BASE, "search_results.json")
SUB_DIR = os.path.join(BASE, "字幕")
PY = r"D:\6_code\13_python\1_python3.11.0\python.exe"
PROXY = "http://127.0.0.1:7892"

with open(IN, encoding="utf-8") as f:
    vids = json.load(f)

# Find the Immortals video
for v in vids:
    if "immortals" in (v.get("title","").lower()) and "counter" in (v.get("title","").lower()):
        print(f"Found Immortals video: {v['id']} | {v['title']} | {v.get('channel')}")

# Videos to retry
retry_ids = [
    ("OesHJ312p1Y", "Valorant Movement Aiming Guide"),
    ("ozGKwdXNLew", "Getting one tapped No time to aim"),
]

# Also find Immortals ID
immortals_id = None
for v in vids:
    t = (v.get("title") or "").lower()
    if "immortals" in t and "counter" in t:
        immortals_id = v["id"]
        immortals_title = v["title"]
        break

if immortals_id:
    retry_ids.append((immortals_id, immortals_title))

def safe_name(s, maxlen=80):
    s = re.sub(r'[\\/:*?"<>|]', "_", s)
    return s[:maxlen]

for vid, title in retry_ids:
    print(f"\nRetrying {vid} | {title[:60]}")
    out_tmpl = os.path.join(SUB_DIR, f"{vid}_{safe_name(title)}")
    cmd = [
        PY, "-m", "yt_dlp",
        "--proxy", PROXY,
        "--write-subs", "--write-auto-subs",
        "--sub-langs", "en.*",
        "--sub-format", "vtt/srt/best",
        "--skip-download",
        "--sleep-requests", "3",
        "-o", out_tmpl + ".%(ext)s",
        f"https://www.youtube.com/watch?v={vid}",
    ]
    for attempt in range(3):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, encoding="utf-8", errors="replace")
            if r.returncode == 0:
                print("  OK")
                break
            else:
                tail = "\n".join(r.stderr.strip().splitlines()[-3:])
                print(f"  attempt {attempt+1} rc={r.returncode}: {tail}")
                time.sleep(10)
        except Exception as e:
            print(f"  attempt {attempt+1} EXC: {e}")
            time.sleep(10)
    time.sleep(5)

print("\nRetry done")
