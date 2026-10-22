# -*- coding: utf-8 -*-
"""YouTube 检索 + 自动字幕：Q024 练枪迁移实战 + 紧张失能"""
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
    "why aim training doesn't transfer to valorant",
    "aim trainer made me worse in game",
    "choking under pressure gaming",
    "how to stop tensing up while aiming",
    "how to stay calm in valorant ranked",
    "nervous aim shaky hands fps",
    "how to play like you practice fps",
    "warm up before ranked valorant routine",
    "muscle tension mouse grip anxiety aiming",
    "aim training vs real game performance transfer",
    "pressure performance motor skill choking",
    "how pros stay calm under pressure esports",
    "kovaaks to valorant transfer",
    "deathmatch vs aim trainer improvement",
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
    ("transfer", 16), ("doesn't transfer", 18), ("not transfer", 18),
    ("chok", 18), ("pressure", 14), ("anxiety", 14), ("nervous", 13),
    ("tense", 15), ("tension", 14), ("tight", 11), ("relax", 11),
    ("calm", 13), ("shaky", 14), ("shake", 12),
    ("practice", 8), ("real game", 14), ("in game", 9), ("ranked", 10),
    ("warm up", 11), ("warmup", 11), ("routine", 7),
    ("aim trainer", 13), ("kovaaks", 11), ("aimlab", 10), ("voltaic", 8),
    ("valorant", 8), ("fps", 6), ("guide", 5), ("how to", 5),
    ("mental", 11), ("mindset", 11), ("psychology", 10),
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
for i, v in enumerate(ranked[:24]):
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
