# -*- coding: utf-8 -*-
"""YouTube 检索 + 自动字幕：Q022 跟枪初速度匹配与加速带"""
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
    "smooth tracking aim guide kovaaks",
    "how to track a moving target aiming lead",
    "voltaic smooth tracking novice guide",
    "why can't I track smoothly mouse aim",
    "tracking aim initial velocity match target",
    "leading the target aim training guide",
    "psalmts kovaaks guide",
    "advanced regen tracking kovaaks",
    "stop losing tracking when target changes direction",
    "aiming prediction vs reaction tracking",
    "mouse control tracking speed matching",
    "how to keep aim locked on target fps",
    "tracking aim acceleration deceleration control",
    "voltaic tracking benchmarks explained",
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
    ("smooth tracking", 16), ("tracking", 10), ("track", 6),
    ("lead", 15), ("predict", 13), ("anticipat", 12), ("velocity", 14),
    ("speed match", 15), ("acceleration", 10), ("deceler", 9),
    ("initial", 10), ("start", 5), ("direction change", 14), ("change direction", 14),
    ("revers", 10), ("strafe", 8), ("strafe aim", 12),
    ("voltaic", 10), ("kovaaks", 10), ("kovaa", 10), ("psalm", 8), ("regen", 9),
    ("guide", 6), ("tutorial", 6), ("how to", 5), ("training", 7), ("aim", 5),
    ("lock", 8), ("stick", 8), ("glue", 8),
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
for i, v in enumerate(ranked[:22]):
    print(f"#{i+1} [{score(v)}] {(v['title'] or '')[:70]} | {v['channel']} | {v['id']}")

with open(os.path.join(OUT, "搜索清单.json"), "w", encoding="utf-8") as f:
    json.dump(ranked, f, ensure_ascii=False, indent=2)

picked = [v for v in ranked if (v.get("duration") or 0) < 3600][:12]
ok = 0
for v in picked:
    print(f"\n--- subs: {v['id']} {(v['title'] or '')[:60]}")
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
