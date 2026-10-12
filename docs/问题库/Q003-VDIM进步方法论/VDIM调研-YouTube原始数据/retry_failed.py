# -*- coding: utf-8 -*-
"""重试3个429失败的YouTube字幕，长间隔。"""
import subprocess, time, os, json

PY = r"D:\6_code\13_python\1_python3.11.0\python.exe"
OUT = os.path.dirname(os.path.abspath(__file__))
PROXY = "http://127.0.0.1:7892"

VIDEOS = [
    ("dar0XyOIEzk", "fix_your_aim_one_week_vdim_lg56"),
    ("xpbJSRd9z8Y", "westproter_immortals_voltaic_bronze"),
    ("W1suJRxp53A", "westproter_mattyow_astra_improve"),
]

print("等待120秒让429冷却...", flush=True)
time.sleep(120)

for vid, name in VIDEOS:
    out_tpl = os.path.join(OUT, name)
    url = f"https://www.youtube.com/watch?v={vid}"
    cmd = [PY, "-m", "yt_dlp", "--no-update", "--proxy", PROXY,
           "--write-subs", "--write-auto-subs", "--sub-lang", "en",
           "--skip-download", "--output", out_tpl, url]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    combined = (p.stdout or "") + (p.stderr or "")
    vtt = out_tpl + ".en.vtt"
    vtt_auto = out_tpl + ".en-orig.vtt"
    if os.path.exists(vtt) or os.path.exists(vtt_auto):
        f = vtt if os.path.exists(vtt) else vtt_auto
        print(f"[OK] {name} ({os.path.getsize(f)}B)", flush=True)
    else:
        print(f"[STILL FAIL] {name}: {combined[-200:]}", flush=True)
    time.sleep(30)
print("RETRY DONE", flush=True)
