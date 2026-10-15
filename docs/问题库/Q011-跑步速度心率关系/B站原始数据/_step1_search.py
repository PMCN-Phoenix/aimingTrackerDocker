# -*- coding: utf-8 -*-
"""Step1: wbi-signed B站搜索, 6组关键词, 结果存 search_raw.json"""
import sys, os, time, json, re, hashlib, urllib.parse
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool
import requests

OUT = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q011-跑步速度心率关系\B站原始数据"
os.makedirs(OUT, exist_ok=True)

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

KEYWORDS = [
    "跑步心率 配速",
    "跑步 心率区间 教学",
    "有氧跑 心率 Z2",
    "马拉松配速 心率",
    "间歇跑 心率 乳酸阈值",
    "VDOT 跑步 配速",
]

def make_session():
    s = requests.Session()
    s.proxies = {"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Referer": "https://search.bilibili.com/",
    })
    pool = BiliCookiePool()
    s.headers["Cookie"] = pool.get_cookie()
    return s, pool

def get_wbi_keys(s):
    nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=20).json()
    wbi = nav["data"]["wbi_img"]
    img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
    mixin = "".join((img + sub)[i] for i in MIXIN)[:32]
    uname = nav["data"].get("uname", "?")
    print(f"[nav] login as: {uname}")
    return mixin

def make_signer(mixin):
    def sign(p):
        p = dict(p)
        p["wts"] = str(int(time.time()))
        q = urllib.parse.urlencode(sorted(p.items()))
        p["w_rid"] = hashlib.md5((q + mixin).encode()).hexdigest()
        return p
    return sign

def strip_em(t):
    return re.sub(r"<[^>]+>", "", t or "")

def main():
    s, pool = make_session()
    mixin = get_wbi_keys(s)
    sign = make_signer(mixin)

    all_results = {}
    for kw in KEYWORDS:
        print(f"\n=== 搜索: {kw} ===")
        items = []
        for page in (1, 2):
            p = sign({"search_type": "video", "keyword": kw, "page": page, "page_size": 30})
            try:
                r = s.get("https://api.bilibili.com/x/web-interface/wbi/search/type",
                          params=p, timeout=25).json()
            except Exception as e:
                print(f"  page{page} error: {e}")
                time.sleep(3)
                continue
            data = r.get("data") or {}
            res = data.get("result") or []
            if not res:
                print(f"  page{page}: empty (code={r.get('code')})")
                break
            for v in res:
                if v.get("type") != "video":
                    continue
                items.append({
                    "keyword": kw,
                    "bvid": v.get("bvid"),
                    "title": strip_em(v.get("title")),
                    "author": v.get("author"),
                    "play": v.get("play"),
                    "danmaku": v.get("video_review"),
                    "duration": v.get("duration"),
                    "pubdate": v.get("pubdate"),
                    "description": v.get("description"),
                    "mid": v.get("mid"),
                })
            print(f"  page{page}: {len(res)} items")
            time.sleep(1.5)
        all_results[kw] = items
        print(f"  -> total {len(items)} for '{kw}'")
        time.sleep(2)

    out_path = os.path.join(OUT, "search_raw.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # 去重统计
    bv_seen = {}
    for kw, items in all_results.items():
        for it in items:
            bv = it["bvid"]
            if bv not in bv_seen:
                bv_seen[bv] = it
                bv_seen[bv]["_hit_kws"] = []
            bv_seen[bv]["_hit_kws"].append(kw)
    print(f"\n[done] raw saved: {out_path}")
    print(f"[done] total unique bvids: {len(bv_seen)}")

if __name__ == "__main__":
    main()
