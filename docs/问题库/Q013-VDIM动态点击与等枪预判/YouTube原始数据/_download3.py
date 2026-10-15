# -*- coding: utf-8 -*-
"""Retry 429-failed videos after long backoff."""
import subprocess, time, os

PY = r"D:\6_code\13_python\1_python3.11.0\python.exe"
OUTDIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\YouTube原始数据\subtitles"
PROXY = "http://127.0.0.1:7892"

VIDEOS = [
    ("F7S-mafDz08", "RiddBTW_smooth_tracking_crashcourse7"),
    ("00meppeDAC0", "WestProter_reload_vs_accuracy_dynamic_clicking"),
    ("wBhCFYuRzk4", "Valkie_click_timing_guide"),
    ("_5u0YN6gHbA", "Lew_floating_heads"),
]

for vid, name in VIDEOS:
    if any(f.startswith(name) and f.endswith('.vtt') for f in os.listdir(OUTDIR)):
        print(f"=== SKIP {name}", flush=True)
        continue
    outtmpl = os.path.join(OUTDIR, name)
    cmd = [
        PY, "-m", "yt_dlp", "--no-update",
        "--proxy", PROXY,
        "--remote-components", "ejs:github",
        "--write-subs", "--sub-lang", "en", "--write-auto-subs",
        "--sub-format", "vtt",
        "--skip-download",
        "--sleep-subtitles", "8",
        "-o", outtmpl,
        f"https://www.youtube.com/watch?v={vid}",
    ]
    print(f"=== {vid} {name}", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print((r.stdout or "")[-300:], flush=True)
    print("[stderr]", (r.stderr or "")[-200:], flush=True)
    files = [f for f in os.listdir(OUTDIR) if f.startswith(name) and f.endswith('.vtt')]
    print("PRODUCED:", files, flush=True)
    time.sleep(20)

print("RETRY DONE")
