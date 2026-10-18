# -*- coding: utf-8 -*-
"""B站评论：抖动 / 手腕 / 握法 相关"""
import sys, json, time, requests, re
sys.path.insert(0, r"D:/11.project/iwen-codex/bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

VIDS = [
    ("BV1uUKp6hEEq", "一瞄准就手抖 控鼠发力错了"),
    ("BV1YM4y1M7Ro", "你真的会选择合适的鼠标握法吗"),
    ("BV1RC411E7Ck", "准星乱抖 瞄头吃力"),
    ("BV1kFJb6eELs", "中文互联网最好的瞄准发力教学"),
    ("BV1318t63Ewc", "弹道飘准星抖 先检查这三项"),
]
KW = ["抖", "手腕", "手指", "握", "张力", "发力", "摩擦", "涩", "卡", "灵敏", "微调", "稳"]


def aid_of(bv):
    s.headers["Cookie"] = pool.get_cookie()
    r = s.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bv}", timeout=20).json()
    if r.get("code") != 0:
        return None, r.get("message")
    return r["data"]["aid"], None


out = {}
for bv, title in VIDS:
    aid, err = aid_of(bv)
    if not aid:
        print(f"  aid失败 {bv} {err}")
        continue
    rows = []
    for pn in (1, 2):
        r = s.get("https://api.bilibili.com/x/v2/reply",
                  params={"type": 1, "oid": aid, "pn": pn, "ps": 20, "sort": 2},
                  timeout=25).json()
        if r.get("code") != 0:
            print(f"  reply {bv} p{pn} code={r.get('code')} {r.get('message')}")
            break
        for rep in r["data"].get("replies") or []:
            rows.append({"msg": rep["content"]["message"], "like": rep["like"],
                         "rc": rep["rcount"]})
        time.sleep(0.8)
    out[bv] = {"title": title, "n": len(rows), "replies": rows}
    print(f"  {bv} {len(rows)} 条")
    time.sleep(1.0)

json.dump(out, open("B站原始数据/评论.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

print("\n=== 命中关键词的评论 ===")
for bv, d in out.items():
    hit = [x for x in d["replies"] if any(k in x["msg"] for k in KW)]
    hit.sort(key=lambda x: -x["like"])
    print(f"\n## {bv} {d['title']}  ({len(hit)}/{d['n']})")
    for x in hit[:6]:
        print(f"  [{x['like']:>4}赞] {x['msg'][:150]}")
