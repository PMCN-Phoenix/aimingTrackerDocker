# -*- coding: utf-8 -*-
"""抓取「变向 / 停枪 / 张力控制」主题视频的字幕。"""
import sys, json, time, requests, re, os
sys.path.insert(0, r"D:/11.project/iwen-codex/bilibili-cookies")
from cookie_manager import BiliCookiePool
pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
SELECTED = [
    ("BV1P6Tu6pEzt", "一个可以让你理解变向的项目"),
    ("BV1A9KpzTEHL", "解决最常见的瞄准难题 张力控制"),
    ("BV1EZ4y1m7EA", "跟枪不平滑 为什么我停枪时会抖"),
    ("BV1mb4y1i7CW", "细说平滑和变向在跟枪中的差别"),
    ("BV1tNj86uET6", "平滑跟枪的秘诀"),
    ("BV1ox4y187nd", "跟枪学习完全攻略指南"),
    ("BV1Ki42zbELL", "xXx 一个细节 提高跟枪上限"),
]

def get_cid(b):
    r = s.get(f"https://api.bilibili.com/x/web-interface/view?bvid={b}", timeout=20).json()
    return (r["data"]["cid"], None) if r.get("code") == 0 else (None, r.get("message"))

def sub_url(b, c):
    r = s.get(f"https://api.bilibili.com/x/player/wbi/v2?bvid={b}&cid={c}", timeout=20).json()
    subs = r.get("data", {}).get("subtitle", {}).get("subtitles", [])
    if not subs:
        return None
    subs.sort(key=lambda x: 0 if "zh" in x.get("lan", "") else 1)
    return subs[0].get("subtitle_url", "")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "B站原始数据", "字幕")
os.makedirs(out, exist_ok=True)
ok = 0
for b, t in SELECTED:
    safe = re.sub(r'[\\/:*?"<>|]', "_", t)[:50]
    p = os.path.join(out, f"{b}_{safe}.txt")
    if os.path.exists(p):
        ok += 1
        continue
    try:
        s.headers["Cookie"] = pool.get_cookie()
        cid, err = get_cid(b)
        if not cid:
            print(f"  cid失败 {b} {err}")
            continue
        u = sub_url(b, cid)
        if not u:
            print(f"  无字幕 {b} {t[:20]}")
            continue
        if u.startswith("//"):
            u = "https:" + u
        j = s.get(u, timeout=20).json()
        txt = "\n".join(i["content"] for i in j.get("body", []))
        open(p, "w", encoding="utf-8").write(f"# {t}\n# {b}\n\n" + txt)
        ok += 1
        print(f"  OK {b} ({len(txt)}字)")
    except Exception as e:
        print(f"  ERR {b} {e}")
    time.sleep(1.5)
print(f"完成 {ok}/{len(SELECTED)}")
