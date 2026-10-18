# -*- coding: utf-8 -*-
"""YouTube 搜索：Q016 疲劳状态下练枪有效性（yt-dlp ytsearch + 代理）"""
import subprocess, json, os, sys, re, time

PY = r"D:\6_code\13_python\1_python3.11.0\python.exe"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "YouTube原始数据")
os.makedirs(OUT, exist_ok=True)

QUERIES = [
    "aim training when tired",
    "mental fatigue aim training",
    "should you practice aim when fatigued",
    "mental fatigue motor skill learning",
    "cognitive fatigue motor learning precision",
    "mental fatigue esports performance",
    "sleep deprivation aim accuracy performance",
    "training when tired strength gains quality",
    "overtraining aim trainer burnout",
    "does mental fatigue ruin practice motor learning",
]

allv = {}
for q in QUERIES:
    print(f"\n=== {q}")
    cmd = [PY, "-m", "yt_dlp", "--no-update", "--proxy", "http://127.0.0.1:7892",
           "--flat-playlist", "--dump-json", f"ytsearch12:{q}"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=180)
    except subprocess.TimeoutExpired:
        print("  超时")
        continue
    n = 0
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        vid = d.get("id")
        if not vid:
            continue
        n += 1
        if vid not in allv:
            allv[vid] = {
                "id": vid,
                "title": d.get("title", ""),
                "channel": d.get("channel") or d.get("uploader", ""),
                "duration": d.get("duration"),
                "views": d.get("view_count"),
                "url": f"https://www.youtube.com/watch?v={vid}",
                "_q": [q],
            }
        elif q not in allv[vid]["_q"]:
            allv[vid]["_q"].append(q)
    print(f"  {n} 条")
    time.sleep(2)

res = sorted(allv.values(), key=lambda v: (len(v["_q"]), v.get("views") or 0), reverse=True)
with open(os.path.join(OUT, "搜索清单.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2)

print(f"\n去重后 {len(res)} 个视频，前 40：")
for i, v in enumerate(res[:40]):
    print(f"  #{i+1} [{len(v['_q'])}q] {v['title'][:64]} | {v['channel']} | {v.get('views')} | {v['id']}")
