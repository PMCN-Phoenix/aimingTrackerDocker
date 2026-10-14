# -*- coding: utf-8 -*-
"""Download en subtitles for the 10 selected videos via yt-dlp + proxy."""
import subprocess, os, time

PY = r"D:\6_code\13_python\1_python3.11.0\python.exe"
PROXY = "http://127.0.0.1:7897"
OUTDIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景\18-拉出去打不到人-YouTube原始数据"

SELECTED = [
    ("IQyXM2qS3-w", "Konpeki - 6 Reasons Why You Whiff in Valorant"),
    ("1vKfPS0OlGA", "Konpeki - An Updated Crosshair Placement Guide 2024"),
    ("LAQJsNfoXbI", "Woohoojin - Peeking is simple if you understand this concept"),
    ("qTiILSy_ItM", "Woohoojin - Radiants peek like this, do you"),
    ("XrIrxWoQKsE", "Woohoojin - Youre peeking this angle wrong"),
    ("goDkhAVKI_Q", "Zapper - Where to Look When Aiming in Valorant"),
    ("M8UKumnWx9E", "Ron Rambo Kim - Crosshair Focus (How to use the Eyes)"),
    ("XNIYrW6dTQM", "4BangerKovaaks - FIX Your Horrible OVERFLICKING"),
    ("ozGKwdXNLew", "THE GUIDE - Getting one tapped No time to aim fix"),
    ("2_U8ElzJ6t4", "Haeyoday - How to swing and hold like a radiant"),
]

def fetch(vid, label):
    outtmpl = os.path.join(OUTDIR, f"字幕\\{vid}_%(title)s.%(ext)s")
    os.makedirs(os.path.join(OUTDIR, "字幕"), exist_ok=True)
    cmd = [
        PY, "-m", "yt_dlp", "--no-update",
        "--proxy", PROXY,
        "--write-subs", "--write-auto-subs", "--sub-lang", "en",
        "--skip-download",
        "--sleep-subtitles", "3",
        "--output", outtmpl,
        f"https://www.youtube.com/watch?v={vid}",
    ]
    print(f"\n=== {vid} :: {label} ===", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    tail = (r.stdout or "")[-400:] + (r.stderr or "")[-400:]
    print(tail, flush=True)
    return r.returncode

def main():
    results = []
    for vid, label in SELECTED:
        code = fetch(vid, label)
        results.append((vid, code))
        time.sleep(2)
    print("\n==== SUMMARY ====")
    for vid, code in results:
        print(f"{vid}: rc={code}")

if __name__ == "__main__":
    main()
