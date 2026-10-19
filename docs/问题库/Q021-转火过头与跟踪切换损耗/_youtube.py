# -*- coding: utf-8 -*-
"""YouTube 检索 + 自动字幕：Q021 转火过头与跟踪切换损耗"""
import os, json, subprocess, sys, re

YT = r"C:/Users/Rose/.workbuddy-ai/binaries/python/envs/default/Scripts/yt-dlp.exe"
NODE = r"C:/Users/Rose/.workbuddy-ai/binaries/node/versions/22.22.2-6/node.exe"
PROXY = "http://127.0.0.1:7892"
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "YouTube原始数据")
SUB = os.path.join(OUT, "字幕")
os.makedirs(SUB, exist_ok=True)

COMMON = [YT, "--proxy", PROXY, "--js-runtimes", "node:" + NODE,
          "--remote-components", "ejs:github", "--no-warnings", "--ignore-errors"]

QUERIES = [
    "target switching overshoot fix aim training",
    "how to stop overshooting flick aim",
    "underflick micro correction aiming guide",
    "voltaic switching routine guide kovaaks",
    "kovaaks target switching tutorial",
    "smooth tracking to flick transition aim",
    "aiming deceleration braking control mouse",
    "speed switching voltaic routine",
    "why does my aim overshoot target",
    "flick accuracy training voltaic",
    "aimer7 target switching guide",
    "mouse control flick stop precision",
]

videos = {}
for q in QUERIES:
    print(f"\n=== {q}")
    cmd = COMMON + [f"ytsearch8:{q}", "--flat-playlist", "--dump-json"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=240, encoding="utf-8", errors="ignore")
        n = 0
        for line in (r.stdout or "").splitlines():
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
            if vid in videos:
                videos[vid]["_q"].append(q)
                continue
            videos[vid] = {
                "id": vid,
                "title": d.get("title", ""),
                "channel": d.get("channel") or d.get("uploader", ""),
                "duration": d.get("duration"),
                "views": d.get("view_count"),
                "upload_date": d.get("upload_date", ""),
                "url": "https://www.youtube.com/watch?v=" + vid,
                "_q": [q],
            }
        print(f"  got {n}")
    except Exception as e:
        print(f"  ERR {e}")

W = [
    ("overshoot", 16), ("over flick", 15), ("overflick", 15), ("underflick", 14),
    ("switch", 12), ("target switching", 16), ("micro correction", 12), ("microcorrection", 12),
    ("flick", 10), ("brake", 8), ("deceler", 9), ("stop", 6), ("precision", 8),
    ("kovaaks", 10), ("kovaa", 10), ("voltaic", 10), ("tracking", 8), ("aim", 5),
    ("guide", 6), ("tutorial", 6), ("how to", 5), ("training", 7),
]
def score(v):
    t = ((v.get("title") or "")).lower()
    s = sum(w for k, w in W if k in t)
    if len(v["_q"]) >= 2:
        s += 5
    vw = v.get("views") or 0
    s += 4 if vw > 300000 else 3 if vw > 80000 else 2 if vw > 15000 else 1 if vw > 3000 else 0
    return s

ranked = sorted(videos.values(), key=score, reverse=True)
for i, v in enumerate(ranked[:20]):
    print(f"#{i+1} [{score(v)}] {v['title'][:70]} | {v['channel']} | {v['id']}")

with open(os.path.join(OUT, "搜索清单.json"), "w", encoding="utf-8") as f:
    json.dump(ranked, f, ensure_ascii=False, indent=2)

# 抓前 10 的自动字幕
picked = [v for v in ranked if (v.get("duration") or 0) < 3600][:10]
ok = 0
for v in picked:
    print(f"\n--- subs: {v['id']} {v['title'][:60]}")
    cmd = COMMON + ["--skip-download", "--write-auto-subs", "--write-subs",
                    "--sub-langs", "en.*,zh.*", "--sub-format", "vtt/srt/best",
                    "-o", os.path.join(SUB, "%(id)s.%(ext)s"), v["url"]]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=240, encoding="utf-8", errors="ignore")
        got = [f for f in os.listdir(SUB) if f.startswith(v["id"])]
        print("  ->", got if got else "无字幕")
        if got:
            ok += 1
    except Exception as e:
        print("  ERR", e)

print(f"\n字幕成功 {ok}/{len(picked)}，视频去重 {len(ranked)}")
