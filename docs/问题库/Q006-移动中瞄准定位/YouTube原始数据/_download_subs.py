# -*- coding: utf-8 -*-
"""Select target videos by title match, then download subtitles."""
import json, os, subprocess, sys, re

BASE = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q006-移动中瞄准定位\YouTube原始数据"
IN = os.path.join(BASE, "search_results.json")
SUB_DIR = os.path.join(BASE, "字幕")
PY = r"D:\6_code\13_python\1_python3.11.0\python.exe"
PROXY = "http://127.0.0.1:7892"

with open(IN, encoding="utf-8") as f:
    vids = json.load(f)

# Selection: match by (channel_substr, title_substr) pairs
SELECTION = [
    ("Woohoojin", "Stop moving like a noob"),
    ("nAts", "12 Tips for Better Movement"),
    ("nAts", "How To Make Aiming 5x Easier"),
    ("Woohoojin", "overaim drill"),
    ("GameLeap", "WIDE SWINGING vs PEEKING"),
    ("Sero", "Get INSANE Movement"),
    ("royalG", "Secrets for Mastering Movement"),
    ("royalG", "why you suck at Peeking"),
    ("Zapper", "Movement Aiming Guide"),
    ("THE GUIDE", "No time to aim"),
    ("Rem", "ULTIMATE Counter Strafing Guide"),
    ("THE GUIDE", "Fixed My Movement"),
    ("Konpeki", "Why You Suck at Peeking"),
    ("Konpeki", "Updated Peeking Guide"),
    ("SC Valorant Guides", "Every Type of Peek"),
    ("Krihzak", "TenZ Explains Why Counter Strafing"),
    ("Sondo301", "Immortals don't counter strafe"),
    ("Sondo301", "shoot in between your strafes"),
    ("Woohoojin", "aim is shaky"),
    ("Woohoojin", "panic in every gunfight"),
]

selected = []
used_titles = set()
for ch_q, title_q in SELECTION:
    ch_ql = ch_q.lower()
    title_ql = title_q.lower()
    found = None
    for v in vids:
        ch = (v.get("channel") or "").lower()
        title = (v.get("title") or "").lower()
        if ch_ql in ch and title_ql in title and v["id"] not in used_titles:
            found = v
            break
    if found:
        selected.append(found)
        used_titles.add(found["id"])
        print(f"OK  [{found['channel']}] {found['title']}  ({found['view_count']:,} views)")
    else:
        print(f"MISS [{ch_q}] / [{title_q}]")

print(f"\nSelected {len(selected)} videos")

# Save selected list
with open(os.path.join(BASE, "selected_videos.json"), "w", encoding="utf-8") as f:
    json.dump(selected, f, ensure_ascii=False, indent=2)

# Download subtitles for each
def safe_name(s, maxlen=80):
    s = re.sub(r'[\\/:*?"<>|]', "_", s)
    return s[:maxlen]

for i, v in enumerate(selected):
    vid = v["id"]
    title = v["title"]
    fname = f"{vid}_{safe_name(title)}"
    print(f"\n[{i+1}/{len(selected)}] {vid} | {title[:60]}")
    out_tmpl = os.path.join(SUB_DIR, fname)
    # yt-dlp: write auto subs + manual subs, en only, skip video
    cmd = [
        PY, "-m", "yt_dlp",
        "--proxy", PROXY,
        "--write-subs", "--write-auto-subs",
        "--sub-langs", "en.*",
        "--sub-format", "vtt/srt/best",
        "--skip-download",
        "-o", out_tmpl + ".%(ext)s",
        f"https://www.youtube.com/watch?v={vid}",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, encoding="utf-8", errors="replace")
        if r.returncode == 0:
            print("  subtitles downloaded")
        else:
            print(f"  rc={r.returncode}")
            # print last lines of stderr
            tail = "\n".join(r.stderr.strip().splitlines()[-5:])
            print(f"  stderr: {tail}")
    except Exception as e:
        print(f"  EXCEPTION: {e}")

print("\n=== Done ===")
