# -*- coding: utf-8 -*-
"""批量抓取 VDIM 调研 YouTube 字幕，走代理，含429退避重试。"""
import subprocess, sys, time, os, json

PY = r"D:\6_code\13_python\1_python3.11.0\python.exe"
OUT = os.path.dirname(os.path.abspath(__file__))
PROXY = "http://127.0.0.1:7892"

# (id, 短名) —— 新抓的目标
VIDEOS = [
    ("dar0XyOIEzk", "fix_your_aim_one_week_vdim_lg56"),
    ("4pWCuQhJ2GI", "riddbtw_apply_aim_training_to_fps"),
    ("xpbJSRd9z8Y", "westproter_immortals_voltaic_bronze"),
    ("CaBeYEZgbhY", "riddbtw_get_voltaic_platinum"),
    ("thlBKM1G9mo", "westproter_what_benchmarks_say"),
    ("RMauBa0bp1Y", "westproter_still_cant_aim"),
    ("BpYCZ5OH7Ik", "lg56_calm_aim_scam_dopai"),
    ("1QwvFbtUi-M", "lg56_take_aim_next_level"),
    ("W1suJRxp53A", "westproter_mattyow_astra_improve"),
    ("4952rP7VKwU", "lg56_vdim_update2"),
    ("ogbHickR7R4", "riddbtw_aim_training_101"),
    ("XQBNQEDSJP0", "lg56_grandmaster_complete"),
    ("fm5N7ljVLM8", "westproter_random_practice_theory8"),
    ("U-rxGWaJWCE", "riddbtw_bad_aiming_days"),
]

results = []
for vid, name in VIDEOS:
    out_tpl = os.path.join(OUT, name)
    url = f"https://www.youtube.com/watch?v={vid}"
    ok = False
    for attempt in range(3):
        cmd = [PY, "-m", "yt_dlp", "--no-update", "--proxy", PROXY,
               "--write-subs", "--write-auto-subs", "--sub-lang", "en",
               "--skip-download", "--output", out_tpl, url]
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        combined = (p.stdout or "") + (p.stderr or "")
        if "429" in combined or "Too Many Requests" in combined or "Sign in to confirm" in combined:
            wait = 60 * (attempt + 1)
            print(f"[429] {name} attempt{attempt+1}, sleep {wait}s", flush=True)
            time.sleep(wait)
            continue
        # 检查是否产出 vtt
        vtt = out_tpl + ".en.vtt"
        vtt_auto = out_tpl + ".en-orig.vtt"
        if os.path.exists(vtt) or os.path.exists(vtt_auto):
            kind = "manual" if os.path.exists(vtt) else "auto"
            size = os.path.getsize(vtt if os.path.exists(vtt) else vtt_auto)
            print(f"[OK] {name} ({kind}, {size}B)", flush=True)
            results.append({"id": vid, "name": name, "status": "ok", "kind": kind, "size": size})
            ok = True
            break
        else:
            # 无字幕（可能视频本身没字幕/没语音）
            if "no subtitles" in combined.lower() or "subtitle" in combined.lower() and "not found" in combined.lower():
                print(f"[NOSUB] {name} — no en subtitles", flush=True)
                results.append({"id": vid, "name": name, "status": "nosub"})
                ok = True
                break
            print(f"[RETRY] {name} attempt{attempt+1}: {combined[-300:]}", flush=True)
            time.sleep(20 * (attempt + 1))
    if not ok:
        results.append({"id": vid, "name": name, "status": "fail"})
    time.sleep(4)  # 逐条间隔，防429

with open(os.path.join(OUT, "fetch_result.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("DONE", flush=True)
