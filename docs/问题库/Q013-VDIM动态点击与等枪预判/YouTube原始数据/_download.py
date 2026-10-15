# -*- coding: utf-8 -*-
"""Download English subtitles for selected new videos."""
import subprocess, time, os, sys

PY = r"D:\6_code\13_python\1_python3.11.0\python.exe"
OUTDIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\YouTube原始数据\subtitles"
PROXY = "http://127.0.0.1:7892"

VIDEOS = [
    ("DcNP0F_gpOQ", "RiddBTW_dynamic_clicking_crashcourse3"),
    ("QXO77LHPV5Q", "RiddBTW_dynamic_clicking_squeakquel4"),
    ("YBbcYMk8-9o", "MattyOW_pure_reactivity_vs_reactive_tracking"),
    ("-7n6q33We28", "MattyOW_speed_matching_precise_tracking"),
    ("nnDHvHPlQ1Y", "Voltaic_dynamic_aim_ep2"),
    ("F7S-mafDz08", "RiddBTW_smooth_tracking_crashcourse7"),
    ("VFjx969H-cg", "RiddBTW_reactive_tracking_crashcourse11"),
    ("ZBNEAgaGjdQ", "christmasiscancelled_moving_dots"),
    ("DP954gl592E", "minigodcs_struggle_moving_targets"),
    ("00meppeDAC0", "WestProter_reload_vs_accuracy_dynamic_clicking"),
    ("cmQh7HKSrdA", "DanielKapadia_tracking_training_method"),
]

os.makedirs(OUTDIR, exist_ok=True)

for vid, name in VIDEOS:
    outtmpl = os.path.join(OUTDIR, name)
    cmd = [
        PY, "-m", "yt_dlp",
        "--no-update",
        "--proxy", PROXY,
        "--remote-components", "ejs:github",
        "--write-subs", "--sub-lang", "en", "--write-auto-subs",
        "--sub-format", "vtt",
        "--skip-download",
        "--sleep-subtitles", "3",
        "-o", outtmpl,
        f"https://www.youtube.com/watch?v={vid}",
    ]
    print(f"=== {vid} {name}", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = (r.stdout or "")[-600:] + "\n[stderr]\n" + (r.stderr or "")[-600:]
    print(tail, flush=True)
    # check what got produced
    files = [f for f in os.listdir(OUTDIR) if f.startswith(name)]
    print("PRODUCED:", files, flush=True)
    time.sleep(4)

print("ALL DONE")
