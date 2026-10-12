# -*- coding: utf-8 -*-
"""
Q002 转火微调 - B站 wbi 多关键词搜索
输出：搜索清单.json（去重后全部候选视频）
"""
import sys, os, time, json, re, hashlib, urllib.parse, requests
from pathlib import Path

sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q002-转火微调\转火微调-B站原始数据")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

KEYWORDS = [
    "转火 微调",
    "瓦洛兰特 转火",
    "VALORANT flick 微调",
    "目标切换 瞄准",
    "target switching aim",
    "跟枪 转火 衔接",
    "瞄准 微调 技巧",
    "定位 精度 瞄准",
    "Kovaak 转火训练",
    "aim trainer target switching",
    "鼠标控制 微调",
    "急停 转火",
    "预瞄 转火 瞄准",
    "反应速度 瞄准 训练",
    "枪法 进阶 技巧",
    "瞄准 肌肉记忆",
    "flick 微调 定位",
    "转火不准 怎么办",
    "快速定位 瞄准",
    "微操 枪法",
]

def make_session(pool):
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Referer": "https://www.bilibili.com/"})
    s.headers["Cookie"] = pool.get_cookie()
    return s

def refresh_wbi_keys(s):
    nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=20).json()
    wbi = nav["data"]["wbi_img"]
    img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
    return "".join((img + sub)[i] for i in MIXIN)[:32]

def sign(p, mixin):
    p = dict(p)
    p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q + mixin).encode()).hexdigest()
    return p

def clean(t):
    return re.sub(r"<[^>]+>", "", t or "")

def parse_dur(s):
    # "MM:SS" or "HH:MM:SS" -> seconds
    if not s: return 0
    parts = [int(x) for x in s.split(":")]
    if len(parts) == 2: return parts[0]*60 + parts[1]
    if len(parts) == 3: return parts[0]*3600 + parts[1]*60 + parts[2]
    return 0

def search_one(s, mixin, kw, page=1):
    p = sign({"search_type": "video", "keyword": kw, "page": page, "page_size": 30}, mixin)
    for attempt in range(3):
        try:
            r = s.get("https://api.bilibili.com/x/web-interface/wbi/search/type",
                      params=p, timeout=25)
            if r.status_code == 412 or '"code":-412' in r.text:
                return None, 412
            d = r.json()
            if d.get("code") != 0:
                return d.get("message"), d.get("code")
            return d.get("data", {}).get("result") or [], 0
        except Exception as e:
            if attempt == 2: return None, str(e)
            time.sleep(2.5)
    return None, "max_retry"

def main():
    pool = BiliCookiePool()
    s = make_session(pool)
    mixin = refresh_wbi_keys(s)
    print(f"[wbi] mixin ok, accounts: {len(pool.accounts)}")

    all_videos = {}  # bvid -> video dict
    kw_stats = []

    for kw in KEYWORDS:
        # refresh cookie if needed
        s.headers["Cookie"] = pool.get_cookie()
        results, err = search_one(s, mixin, kw, 1)
        if err == 412:
            pool.report_412()
            print(f"[412] {kw} -> switching account, retry...")
            time.sleep(3)
            s.headers["Cookie"] = pool.get_cookie()
            results, err = search_one(s, mixin, kw, 1)
        if results is None:
            print(f"[FAIL] {kw}: {err}")
            kw_stats.append({"kw": kw, "count": 0, "err": str(err)})
            time.sleep(2)
            continue
        pool.report_success()
        cnt = 0
        for v in results:
            bvid = v.get("bvid")
            if not bvid: continue
            item = {
                "bvid": bvid,
                "title": clean(v.get("title")),
                "author": v.get("author"),
                "play": v.get("play") or 0,
                "duration": v.get("duration"),
                "_dur_s": parse_dur(v.get("duration")),
                "pubdate": v.get("pubdate"),
                "description": clean(v.get("description"))[:300],
                "kw_hit": [kw] if bvid not in all_videos else all_videos[bvid].get("kw_hit", []) + [kw],
            }
            if bvid in all_videos:
                # merge kw hits, keep max play
                all_videos[bvid]["kw_hit"] = list(set(all_videos[bvid]["kw_hit"] + [kw]))
                if (v.get("play") or 0) > all_videos[bvid]["play"]:
                    all_videos[bvid]["play"] = v.get("play") or 0
            else:
                all_videos[bvid] = item
                cnt += 1
        kw_stats.append({"kw": kw, "count": len(results), "new": cnt})
        print(f"[OK] {kw}: {len(results)} results, {cnt} new (total {len(all_videos)})")
        time.sleep(1.5)  # 限速

    out = {
        "keywords": KEYWORDS,
        "kw_stats": kw_stats,
        "total_unique": len(all_videos),
        "videos": list(all_videos.values()),
    }
    (OUT_DIR / "搜索清单.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[DONE] total unique videos: {len(all_videos)}")
    print(f"[OUT] {(OUT_DIR / '搜索清单.json')}")

if __name__ == "__main__":
    main()
