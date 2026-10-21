# -*- coding: utf-8 -*-
"""Q023 精选字幕抓取"""
import sys, json, time, os, re, requests
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

BASE = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q023-手部保暖策略与成本效益"
SUB_DIR = os.path.join(BASE, "B站原始数据", "字幕")
os.makedirs(SUB_DIR, exist_ok=True)

PICKS = [
    ("BV1VACHYYEgR", "南方人冬天FPS不菜的法宝-电竞房三件"),
    ("BV1jw41137rs", "冬天打游戏手冷怎么办"),
    ("BV1mxUZBhEy1", "冬天打游戏手部保暖2.0"),
    ("BV1wZFQzvEJ3", "百元电加热手套拆解实测"),
    ("BV1h64y1H7U8", "电加热手套or智商税"),
    ("BV1Ut421b7XW", "电加热手套用一个冬季后的感受"),
    ("BV1xc41147Fj", "耗时一月测冬季爆款取暖神器"),
    ("BV1dAzEB6EHt", "十块钱解决手冷"),
    ("BV1GK421h7kW", "瓦洛兰特瞄准永远埋葬在冬天"),
    ("BV1NhrvB5ETs", "36元USB加热手套测评"),
    ("BV1BvytYfEah", "手环对FPS技术与体验"),
    ("BV1JP4y1Q7my", "电加热手套踩坑(骑行向反面对照)"),
]

def get_cid(bvid):
    c = pool.get_cookie()
    s.headers["Cookie"] = c
    r = s.get("https://api.bilibili.com/x/player/pagelist", params={"bvid": bvid}, timeout=20)
    j = r.json()
    if j.get("code") == 0 and j.get("data"):
        return j["data"][0]["cid"]
    return None

def get_subtitle(bvid, cid):
    c = pool.get_cookie()
    s.headers["Cookie"] = c
    p = {"bvid": bvid, "cid": cid}
    r = s.get("https://api.bilibili.com/x/player/wbi/v2", params=p, timeout=20)
    j = r.json()
    if j.get("code") != 0:
        return None, f"code={j.get('code')}"
    subs = (j.get("data", {}).get("subtitle", {}) or {}).get("subtitles", [])
    if not subs:
        return None, "no-subtitle"
    subs.sort(key=lambda x: 0 if "ai" in (x.get("lan") or "") else 1)
    url = subs[0].get("subtitle_url") or ""
    if url.startswith("//"):
        url = "https:" + url
    if not url:
        return None, "empty-url"
    rr = requests.get(url, timeout=20, headers={"User-Agent": s.headers["User-Agent"]})
    try:
        body = rr.json().get("body", [])
    except Exception:
        return None, "json-fail"
    lines = [b.get("content", "") for b in body]
    return "\n".join(lines), f"{len(lines)} lines"

ok = 0
for bvid, name in PICKS:
    try:
        cid = get_cid(bvid)
        if not cid:
            print(f"[跳过] {name} ({bvid}) 无 cid")
            continue
        time.sleep(0.6)
        txt, info = get_subtitle(bvid, cid)
        if not txt:
            print(f"[无字幕] {name} ({bvid}) {info}")
            continue
        safe = re.sub(r'[\\/:*?"<>|]', "_", name)
        p = os.path.join(SUB_DIR, f"{safe}__{bvid}.txt")
        with open(p, "w", encoding="utf-8") as f:
            f.write(txt)
        print(f"[OK] {name} ({bvid}) {info}")
        ok += 1
    except Exception as e:
        print(f"[错误] {name} ({bvid}) {str(e)[:80]}")
    time.sleep(1.2)

print(f"\n成功 {ok}/{len(PICKS)}")
