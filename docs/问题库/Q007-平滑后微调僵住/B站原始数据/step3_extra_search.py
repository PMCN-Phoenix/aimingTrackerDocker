# -*- coding: utf-8 -*-
"""
Step3: 追加搜索蹲拉peek预瞄偏差场景
"""
import sys, os, re, json, time, hashlib, urllib.parse
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool
import requests

OUT_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q007-平滑后微调僵住\B站原始数据"

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]
PROXIES = {"http": "http://127.0.0.1:7892", "https": "http://127.0.0.1:7892"}

EXTRA_KEYWORDS = [
    "蹲拉 peek 预瞄 偏差 修正",
    "crouch peek 瞄准 甩枪 卡住",
    "预瞄 不准 大角度 拉枪 僵硬",
    "蹲着瞄准 站起来 瞄准 切换",
    "peek 预瞄 失误 补救 flick",
    "急停 开枪 节奏 蹲拉",
    # 补充换说法
    "蹲拉 急停 瞄准 教学",
    "预瞄差 拉枪 补救 FPS",
    "crouch peek 预瞄 技巧",
    "蹲peek 站起来 开枪 节奏",
]

def clean_html(t):
    return re.sub(r"<[^>]+>", "", t or "")

def make_session(pool):
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
    })
    s.proxies.update(PROXIES)
    s.headers["Cookie"] = pool.get_cookie()
    return s

def get_wbi_keys(s):
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

def search_one(s, mixin, kw, pool, page=1):
    p = sign({"search_type": "video", "keyword": kw, "page": page, "page_size": 30}, mixin)
    for attempt in range(3):
        try:
            r = s.get("https://api.bilibili.com/x/web-interface/wbi/search/type", params=p, timeout=25)
            d = r.json()
            if d.get("code") == 0:
                pool.report_success()
                return d.get("data") or {}
            if d.get("code") == -412:
                pool.report_412()
                s.headers["Cookie"] = pool.get_cookie()
                time.sleep(3)
                continue
            time.sleep(2)
        except Exception as e:
            print(f"  [!] exception: {e}")
            time.sleep(3)
    return {}

def duration_to_sec(dur):
    parts = dur.split(":")
    try:
        if len(parts) == 2: return int(parts[0])*60 + int(parts[1])
        elif len(parts) == 3: return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
    except: return 0
    return 0

def score_extra(v):
    t = (v.get("title") or "") + " " + (v.get("description") or "")
    t_low = t.lower()
    s = 0.0
    weights = [
        ("蹲拉", 6), ("蹲peek", 5), ("crouch", 4), ("peek", 4),
        ("预瞄", 5), ("准星放置", 4), ("crosshair", 4),
        ("偏差", 3), ("失误", 2), ("补救", 4), ("修正", 3),
        ("甩枪", 3), ("flick", 4), ("拉枪", 3), ("大角度", 3),
        ("急停", 4), ("开枪节奏", 4), ("站起来", 3), ("蹲起", 3),
        ("僵硬", 3), ("卡住", 3),
        ("无畏", 2), ("valorant", 2), ("csgo", 2), ("cs2", 2),
        ("技巧", 1), ("教学", 1), ("瞄准", 2),
    ]
    for kw, w in weights:
        if kw.lower() in t_low: s += w
    play = v.get("play") or 0
    if play > 100000: s += 3
    elif play > 30000: s += 2
    elif play > 5000: s += 0.5
    elif play < 1000: s -= 2
    dur_s = v.get("_dur_s", 0)
    if dur_s < 45: s -= 1.5
    return s

def main():
    pool = BiliCookiePool()
    s = make_session(pool)
    mixin = get_wbi_keys(s)
    print(f"[OK] wbi mixin={mixin[:8]}...")

    # 加载已有搜索清单去重
    existing_path = os.path.join(OUT_DIR, "搜索清单.json")
    existing = {}
    if os.path.exists(existing_path):
        with open(existing_path, "r", encoding="utf-8") as f:
            for v in json.load(f):
                existing[v["bvid"]] = v

    all_videos = dict(existing)

    for kw in EXTRA_KEYWORDS:
        print(f"\n=== 追加搜索: {kw} ===")
        data = search_one(s, mixin, kw, pool, page=1)
        results = data.get("result") or []
        cnt_new = 0
        for v in results:
            if v.get("type") and v["type"] != "video": continue
            bvid = v.get("bvid")
            if not bvid: continue
            title = clean_html(v.get("title"))
            dur = v.get("duration") or ""
            item = {
                "bvid": bvid, "title": title, "author": v.get("author"),
                "play": v.get("play"), "duration": dur, "_dur_s": duration_to_sec(dur),
                "description": clean_html(v.get("description") or ""),
                "pubdate": v.get("pubdate"), "tag": v.get("tag", ""),
                "search_kw": [kw], "is_extra": True,
            }
            if bvid in all_videos:
                all_videos[bvid]["search_kw"].append(kw)
                all_videos[bvid]["is_extra"] = all_videos[bvid].get("is_extra", False)
            else:
                all_videos[bvid] = item
                cnt_new += 1
        print(f"  本页 {len(results)} 条, 新增 {cnt_new}, 累计 {len(all_videos)}")
        time.sleep(1.5)

    # 对新视频打分
    for bvid, v in all_videos.items():
        if "score" not in v:
            v["score"] = score_extra(v)

    ranked = sorted(all_videos.values(), key=lambda x: -x["score"])

    # 保存合并后的清单
    with open(existing_path, "w", encoding="utf-8") as f:
        json.dump(ranked, f, ensure_ascii=False, indent=2)

    # 只打印新搜索出来的 top 30
    new_videos = [v for v in ranked if v.get("is_extra")]
    print(f"\n=== 追加搜索新增 Top 30 ===")
    for i, v in enumerate(new_videos[:30]):
        print(f"{i+1:2d}. [{v['score']:5.1f}] {v['bvid']} | 播放{v.get('play'):>8} | {v['duration']:>8} | {v['author'][:12]:<12} | {v['title'][:55]}")

    print(f"\n[OK] 合并清单已保存: {existing_path}, 总数 {len(ranked)}")

if __name__ == "__main__":
    main()
