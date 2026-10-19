# -*- coding: utf-8 -*-
"""Pokevox Easy LG56 快打方式检索（B站 + YouTube）"""
import os, re, json, time, requests, sys, subprocess

BASE = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q004-场景技术问题\Pokevox快打检索"
os.makedirs(os.path.join(BASE, "字幕"), exist_ok=True)
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

# ---------- B 站 ----------
BILI_QS = ["Pokevox", "LG56 kovaaks", "kovaaks 电枪", "kovaak LG 跟枪",
           "quaker bot strafes", "kovaaks 移动靶 点击", "闪电枪 跟枪 kovaak",
           "kovaaks 高分 跟枪", " voltaic 字幕", "pokeball kovaaks"]
bili = []
for q in BILI_QS:
    try:
        from bilibili_search import search  # 若无此模块则走简易接口
    except Exception:
        search = None
    if search is None:
        # 简易 WBI 免签接口（web-interface/search/type 对部分关键词可用）
        try:
            r = s.get("https://api.bilibili.com/x/web-interface/search/all/v2",
                      params={"keyword": q}, timeout=15,
                      headers={"Cookie": pool.get_cookie(), "Referer": "https://www.bilibili.com"}).json()
            if r.get("code") != 0:
                print("[bili]", q, "->", r.get("message"))
                continue
            items = [x for x in r["data"].get("result", []) if x.get("result_type") == "video"]
        except Exception as e:
            print("[bili] ERR", q, e)
            continue
    else:
        items = search(q)
    print("[bili] %s -> %d" % (q, len(items)))
    for it in items[:8]:
        bili.append({"kw": q, "bvid": it.get("bvid"), "title": re.sub("<[^>]+>", "", it.get("title", "")),
                     "author": it.get("author"), "play": it.get("play"),
                     "desc": (it.get("description") or "")[:120]})

seen, uniq = set(), []
for b in bili:
    if b["bvid"] and b["bvid"] not in seen:
        seen.add(b["bvid"]); uniq.append(b)
print("B站去重", len(uniq))
for i, b in enumerate(uniq[:30]):
    print("#%d [%s] %s | %s | %s" % (i + 1, b["bvid"], b["title"][:52], b["author"], b["play"]))
json.dump(uniq, open(os.path.join(BASE, "b站搜索.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- YouTube ----------
YT = r"C:/Users/Rose/.workbuddy-ai/binaries/python/envs/default/Scripts/yt-dlp.exe"
NODE = r"C:/Users/Rose/.workbuddy-ai/binaries/node/versions/22.22.2-6/node.exe"
PROXY = "http://127.0.0.1:7892"
COMMON = [YT, "--proxy", PROXY, "--js-runtimes", "node:" + NODE,
          "--remote-components", "ejs:github", "--no-warnings", "--ignore-errors"]
YT_QS = ["Pokevox LG56 kovaaks", "LG56 kovaaks playlist", "kovaaks LG tracking high score",
        "quaker bot long strafes kovaaks", "kovaaks lightning gun tracking",
        "pokeball scenario kovaaks", "voltaic LG tracking guide"]
videos = {}
for q in YT_QS:
    print("\n[yt]", q)
    cmd = COMMON + [f"ytsearch8:{q}", "--flat-playlist", "--dump-json"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180, encoding="utf-8", errors="ignore")
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
                videos[vid]["_q"].append(q); continue
            videos[vid] = {"id": vid, "title": d.get("title", ""), "channel": d.get("channel") or d.get("uploader", ""),
                           "duration": d.get("duration"), "views": d.get("view_count"),
                           "url": "https://www.youtube.com/watch?v=" + vid, "_q": [q]}
        print("   got", n)
    except Exception as e:
        print("   ERR", e)

ranked = sorted(videos.values(), key=lambda v: (v.get("views") or 0), reverse=True)
print("\n=== YouTube 按播放量 ===")
for i, v in enumerate(ranked[:20]):
    print("#%d %6s | %s | %s | %s" % (i + 1, v.get("views"), (v["title"] or "")[:60], v["channel"], v["id"]))
json.dump(ranked, open(os.path.join(BASE, "youtube搜索.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 抓前 6 条字幕
SUB = os.path.join(BASE, "字幕")
picked = [v for v in ranked if (v.get("duration") or 0) < 3600][:6]
for v in picked:
    cmd = COMMON + ["--skip-download", "--write-auto-subs", "--write-subs", "--sub-langs", "en.*,zh.*",
                    "--sub-format", "vtt/srt/best", "-o", os.path.join(SUB, "%(id)s.%(ext)s"), v["url"]]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=180, encoding="utf-8", errors="ignore")
        got = [f for f in os.listdir(SUB) if f.startswith(v["id"])]
        print("subs:", v["id"], "->", got if got else "无字幕")
    except Exception as e:
        print("subs ERR", v["id"], e)
print("\n完成")
