# -*- coding: utf-8 -*-
"""Q019 精选字幕抓取"""
import sys, json, time, os, re, requests
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

BASE = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q019-练枪与健身训练周期耦合"
SUB_DIR = os.path.join(BASE, "B站原始数据", "字幕")
os.makedirs(SUB_DIR, exist_ok=True)

PICKS = [
    ("BV1hTBCYkEmY", "前臂力量训练与FPS瞄准能力"),
    ("BV1XjbX6VEZa", "健身对于FPS游戏的影响"),
    ("BV1k2VrzuEjD", "健身真的对瞄准有帮助吗-GUS"),
    ("BV1EK4y1P7VD", "力量训练周期性计划思路"),
    ("BV1J34y1b7iK", "超量恢复原理与训练规划"),
    ("BV1vN4y1U76D", "超量恢复理论争议"),
    ("BV1hc411478x", "训练过度的4个症状"),
    ("BV1Zm4y1F7Kn", "手腕酸痛康复与鼠标手"),
    ("BV1Vs4y1c7i3", "前臂区域疼痛缓解"),
    ("BV1Ds421P7CG", "运动后酸痛与炎症"),
    ("BV1XCaJ64EYG", "少练一点反而练得更壮"),
    ("BV12h4y1X7hi", "爱打游戏对健身有影响吗"),
    ("BV1rfwCzUE18", "打完游戏就健身健完身就打游戏"),
    ("BV149HfetErB", "该摆烂时就安心摆烂"),
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
    sub = j.get("data", {}).get("subtitle", {})
    subs = sub.get("subtitles") or []
    if not subs:
        return None, "无字幕"
    # 优先中文
    subs_sorted = sorted(subs, key=lambda x: 0 if "zh" in (x.get("lan") or "") else 1)
    target = subs_sorted[0]
    url = target.get("subtitle_url") or ""
    if url.startswith("//"):
        url = "https:" + url
    if not url:
        return None, "无字幕URL"
    rr = s.get(url, timeout=20)
    data = rr.json()
    lines = []
    for b in data.get("body", []):
        lines.append(b.get("content", ""))
    return "\n".join(lines), "ok:" + (target.get("lan") or "")

ok = 0
for bvid, label in PICKS:
    try:
        cid = get_cid(bvid)
        if not cid:
            print(f"  [{bvid}] 无 cid")
            continue
        text, st = get_subtitle(bvid, cid)
        if not text:
            print(f"  [{bvid}] {label[:20]} -> {st}")
            time.sleep(1.0)
            continue
        safe = re.sub(r'[\\/:*?"<>|]', "_", label)[:40]
        fn = os.path.join(SUB_DIR, f"{bvid}_{safe}.txt")
        with open(fn, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"  [{bvid}] {label[:20]} -> {st} ({len(text)}字)")
        ok += 1
        time.sleep(1.0)
    except Exception as e:
        print(f"  [{bvid}] 错误: {e}")
print(f"\n完成: {ok}/{len(PICKS)}")
