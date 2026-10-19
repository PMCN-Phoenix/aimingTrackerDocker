# -*- coding: utf-8 -*-
"""Q019 B站评论区抓取：健身×FPS 高相关视频"""
import sys, json, time, os, requests, re
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

BASE = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q019-练枪与健身训练周期耦合"
OUT = os.path.join(BASE, "B站原始数据", "评论.json")

TARGETS = [
    ("BV1XjbX6VEZa", "健身对于FPS游戏的影响-MYCRUSH"),
    ("BV1k2VrzuEjD", "健身真的对瞄准有帮助吗-枫的外设GUS"),
    ("BV1J34y1b7iK", "超量恢复原理与训练规划"),
    ("BV12h4y1X7hi", "爱打游戏对健身有影响吗"),
]

def get(path, params, retries=3):
    for i in range(retries):
        try:
            s.headers["Cookie"] = pool.get_cookie()
            r = s.get(path, params=params, timeout=20)
            return r.json()
        except Exception:
            if i == retries - 1:
                return None
            time.sleep(2)

allrows = []
for bvid, label in TARGETS:
    v = get("https://api.bilibili.com/x/web-interface/view", {"bvid": bvid})
    if not v or v.get("code") != 0:
        print(f"[{bvid}] 视频信息失败")
        continue
    aid = v["data"]["aid"]
    title = v["data"]["title"]
    time.sleep(1)
    j = get("https://api.bilibili.com/x/v2/reply", {"type": 1, "oid": aid, "sort": 2, "ps": 20, "pn": 1})
    if not j or j.get("code") != 0:
        print(f"[{bvid}] 评论失败 code={j.get('code') if j else 'none'}")
        continue
    reps = (j.get("data") or {}).get("replies") or []
    print(f"[{bvid}] {title[:30]} -> {len(reps)} 条")
    for r in reps:
        allrows.append({
            "bvid": bvid,
            "video": title,
            "user": r["member"]["uname"],
            "like": r.get("like", 0),
            "time": r.get("ctime"),
            "content": r["content"]["message"],
        })
    time.sleep(1.2)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(allrows, f, ensure_ascii=False, indent=2)

print(f"\n共 {len(allrows)} 条 -> {OUT}")
for r in sorted(allrows, key=lambda x: -x["like"])[:22]:
    print(f"  [{r['like']}赞] {r['content'][:88]}")
