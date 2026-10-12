# -*- coding: utf-8 -*-
"""B站 VDIM 主题 wbi 多关键词搜索 + 去重打分。"""
import sys, os, time, json, re, hashlib, urllib.parse
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
import requests
from cookie_manager import BiliCookiePool

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

OUT = os.path.dirname(os.path.abspath(__file__))

KEYWORDS = [
    "VDIM", "VDIM 训练", "Voltaic 瞄准", "跟枪 进步",
    "瞄准训练 方法论", "Kovaak 进步", "动态瞄准 训练", "反应跟枪",
    "瞄准 瓶颈", "枪法 提升 方法", "练枪 效率", "瞄准 评估",
    "aim trainer 进步", "tracking aim 训练",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
}

pool = BiliCookiePool()
s = requests.Session()
s.headers.update(HEADERS)
s.headers["Cookie"] = pool.get_cookie()

# 拿 wbi key
nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=20).json()
wbi = nav["data"]["wbi_img"]
img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
MIXIN_KEY = "".join((img + sub)[i] for i in MIXIN)[:32]

def sign(p):
    p = dict(p)
    p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q + MIXIN_KEY).encode()).hexdigest()
    return p

def clean(t):
    return re.sub(r"<[^>]+>", "", t or "")

def dur_sec(d):
    m = re.match(r"(?:(\d+):)?(\d+):(\d+)", d or "")
    if not m:
        return 0
    h, mm, ss = m.groups()
    return (int(h or 0) * 3600) + int(mm) * 60 + int(ss)

all_videos = {}
for kw in KEYWORDS:
    for page in (1, 2):
        try:
            p = sign({"search_type": "video", "keyword": kw, "page": page, "page_size": 30,
                      "order": "totalrank"})
            r = s.get("https://api.bilibili.com/x/web-interface/wbi/search/type",
                      params=p, timeout=25)
            if r.status_code == 412 or '"code":-412' in r.text:
                pool.report_412()
                s.headers["Cookie"] = pool.get_cookie()
                time.sleep(3)
                continue
            data = r.json().get("data") or {}
            results = data.get("result") or []
            if not results:
                break
            pool.report_success()
            for v in results:
                bvid = v.get("bvid")
                if not bvid:
                    continue
                if bvid not in all_videos:
                    all_videos[bvid] = {
                        "bvid": bvid,
                        "title": clean(v.get("title")),
                        "author": v.get("author"),
                        "play": v.get("play", 0),
                        "duration": v.get("duration", ""),
                        "dur_s": dur_sec(v.get("duration", "")),
                        "pubdate": v.get("pubdate", 0),
                        "desc": clean(v.get("description", ""))[:300],
                        "keywords": [],
                    }
                all_videos[bvid]["keywords"].append(kw)
            time.sleep(1.5)
        except Exception as e:
            print(f"[ERR] {kw} p{page}: {e}", flush=True)
            time.sleep(3)
            continue
    print(f"[OK] kw={kw} | total={len(all_videos)}", flush=True)
    time.sleep(1.5)

# 打分
WEIGHTS = [
    ("vdim", 10), ("voltaic", 8), ("沃泰克", 8), ("跟枪", 5), ("tracking", 5),
    ("kovaak", 7), ("科瓦克", 7), ("瞄准", 3), ("练枪", 3), ("靶场", 2),
    ("进步", 5), ("瓶颈", 6), ("提升", 4), ("方法论", 5), ("训练计划", 4),
    ("反应", 3), ("动态瞄准", 5), ("评估", 4), ("benchmark", 6), ("基准", 5),
    ("aim", 2), ("攻略", 2), ("教学", 2),
]

def score(v):
    t = (v["title"] + " " + v["desc"]).lower()
    sc = 0.0
    for k, w in WEIGHTS:
        if k in t:
            sc += w
    p = v["play"] or 0
    sc += 3 if p > 200000 else 2 if p > 50000 else 1.2 if p > 10000 else 0.5 if p > 3000 else -1
    if v["dur_s"] < 45:
        sc -= 1.5
    if v["dur_s"] > 3600:
        sc -= 0.5
    # 关键词命中数加权
    sc += min(len(v["keywords"]), 5) * 1.5
    return sc

for bvid, v in all_videos.items():
    v["score"] = round(score(v), 2)

ranked = sorted(all_videos.values(), key=lambda x: -x["score"])
with open(os.path.join(OUT, "search_results.json"), "w", encoding="utf-8") as f:
    json.dump(ranked, f, ensure_ascii=False, indent=2)

print(f"\n=== 去重后 {len(ranked)} 个视频，Top30 ===", flush=True)
for v in ranked[:30]:
    print(f'{v["score"]:6.1f} | {v["bvid"]} | {v["play"]:>8} | {v["duration"]:>8} | {v["title"][:40]}', flush=True)
