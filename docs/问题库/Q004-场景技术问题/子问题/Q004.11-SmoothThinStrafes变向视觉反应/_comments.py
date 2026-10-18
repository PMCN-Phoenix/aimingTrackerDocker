# -*- coding: utf-8 -*-
"""抓取「眼睛/阅读目标/变向」主题视频的高赞评论。"""
import sys, time, json, requests, os
sys.path.insert(0, r"D:/11.project/iwen-codex/bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

TARGETS = [
    ("BV1654y1d73x", "APEX跟枪不是无数次的定位"),
    ("BV1zUjY6iEzs", "中文互联网最好的瞄准教学"),
    ("BV1Kq4y1E7oU", "5分钟教你如何锻炼自己的眼睛"),
    ("BV17pMg6mEy8", "一招制胜 高级FPS眼部追踪"),
    ("BV1eehiz9EEc", "目标一动就马枪 动态定位"),
]

def get_aid(b):
    r = s.get(f"https://api.bilibili.com/x/web-interface/view?bvid={b}", timeout=20).json()
    if r.get("code") != 0:
        return None, r.get("message")
    return r["data"]["aid"], None

out = {}
for b, t in TARGETS:
    try:
        s.headers["Cookie"] = pool.get_cookie()
        aid, err = get_aid(b)
        if not aid:
            print(f"  aid失败 {b} {err}")
            continue
        # 注意：wbi/main 端点 2026-10 起返回 -403，legacy /x/v2/reply 仍可用
        params = {"oid": aid, "type": 1, "pn": 1, "ps": 20, "sort": 2}
        r = s.get("https://api.bilibili.com/x/v2/reply", params=params, timeout=25).json()
        if r.get("code") != 0:
            print(f"  评论失败 {b} code={r.get('code')} {r.get('message')}")
            continue
        reps = r["data"].get("replies") or []
        rows = []
        for c in reps:
            rows.append({
                "uname": c["member"]["uname"],
                "like": c["like"],
                "message": c["content"]["message"],
                "subs": [{"uname": x["member"]["uname"], "like": x["like"],
                          "message": x["content"]["message"]} for x in (c.get("replies") or [])],
            })
        out[b] = {"title": t, "aid": aid, "count": r["data"]["page"]["count"], "comments": rows}
        print(f"  OK {b} {t[:18]} 顶层{len(rows)}条 / 总{r['data']['page']['count']}")
    except Exception as e:
        print(f"  ERR {b} {e}")
    time.sleep(1.5)

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "B站原始数据", "评论.json")
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n写入 {p}（{len(out)} 个视频）")
