# -*- coding: utf-8 -*-
"""Second batch: retry failed + new videos for sub-questions 1 & 2."""
import subprocess, time, os

PY = r"D:\6_code\13_python\1_python3.11.0\python.exe"
OUTDIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\YouTube原始数据\subtitles"
PROXY = "http://127.0.0.1:7892"

VIDEOS = [
    ("F7S-mafDz08", "RiddBTW_smooth_tracking_crashcourse7"),
    ("ZBNEAgaGjdQ", "christmasiscancelled_moving_dots"),
    ("DP954gl592E", "minigodcs_struggle_moving_targets"),
    ("00meppeDAC0", "WestProter_reload_vs_accuracy_dynamic_clicking"),
    ("cmQh7HKSrdA", "DanielKapadia_tracking_training_method"),
    # sub-question 2: Floating Heads Timing
    ("wBhCFYuRzk4", "Valkie_click_timing_guide"),
    ("_5u0YN6gHbA", "Lew_floating_heads"),
    # sub-question 1: jitter / micro-adjustment
    ("oVOL2u2tg-0", "christmasiscancelled_thin_gauntlet"),
    ("6pJGSYXcbCc", "Kovaaks_fix_shaky_jittery_aim"),
    ("Hj8fYdea4tQ", "4Banger_fix_microadjusting"),
    ("XNIYrW6dTQM", "4Banger_fix_overflicking"),
    ("feUxul6TGyQ", "4Banger_shaky_aim_tracking_7solutions"),
]

os.makedirs(OUTDIR, exist_ok=True)

for vid, name in VIDEOS:
    # skip if already downloaded
    if any(f.startswith(name) and f.endswith('.vtt') for f in os.listdir(OUTDIR)):
        print(f"=== SKIP (exists) {vid} {name}", flush=True)
        continue
    outtmpl = os.path.join(OUTDIR, name)
    cmd = [
        PY, "-m", "yt_dlp",
        "--no-update",
        "--proxy", PROXY,
        "--remote-components", "ejs:github",
        "--write-subs", "--sub-lang", "en", "--write-auto-subs",
        "--sub-format", "vtt",
        "--skip-download",
        "--sleep-subtitles", "5",
        "-o", outtmpl,
        f"https://www.youtube.com/watch?v={vid}",
    ]
    print(f"=== {vid} {name}", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = (r.stdout or "")[-400:] + "\n[stderr]\n" + (r.stderr or "")[-300:]
    print(tail, flush=True)
    files = [f for f in os.listdir(OUTDIR) if f.startswith(name) and f.endswith('.vtt')]
    print("PRODUCED:", files, flush=True)
    time.sleep(8)

print("BATCH2 DONE")
