# -*- coding: utf-8 -*-
"""Step5: 抓 4 个高互动视频的评论（wbi 评论接口）"""
import sys, os, time, json, hashlib, urllib.parse
import requests

OUT = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q011-跑步速度心率关系\B站原始数据"
COOKIE_FILE = r"D:\11.project\iwen-codex\bilibili-cookies\account3.txt"

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

cookie = open(COOKIE_FILE, encoding="utf-8-sig").read().strip()
s = requests.Session()
s.proxies = {"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Cookie": cookie,
})
nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=20).json()
print(f"[login] {nav['data'].get('uname')}")
wbi = nav["data"]["wbi_img"]
img = wbi["img_url"].rsplit("/",1)[-1].split(".")[0]
sub = wbi["sub_url"].rsplit("/",1)[-1].split(".")[0]
MIX = "".join((img+sub)[i] for i in MIXIN)[:32]

def sign(p):
    p = dict(p); p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q+MIX).encode()).hexdigest()
    return p

# 从 subtitle_status.json 读 aid
status = json.load(open(os.path.join(OUT, "subtitle_status.json"), encoding="utf-8"))
by_bv = {r["bvid"]: r for r in status}

# 选 4 个高互动/重要视频抓评论
TARGETS = [
    ("BV1Vm41127RA", "鞋吧-运动心率"),
    ("BV1zo4y1m7uN", "子章老师-心率使用"),
    ("BV1QgPDzpE7x", "斌哥-无效有氧到无氧"),
    ("BV1NkoLBFEdg", "西卡卡卡-跑圈谣言"),
]

all_comments = {}
for bv, label in TARGETS:
    aid = by_bv[bv].get("aid")
    print(f"\n=== {bv} ({label}) aid={aid} ===")
    if not aid:
        print("  no aid, skip"); continue
    items = []
    try:
        for pn in range(1, 6):  # 最多5页
            q = sign({"oid": aid, "type": 1, "pn": pn, "ps": 20, "sort": 2})
            d = s.get("https://api.bilibili.com/x/v2/reply/wbi/main", params=q,
                      headers={"Referer": f"https://www.bilibili.com/video/{bv}/"}, timeout=20).json()
            dd = d.get("data") or {}
            reps = dd.get("replies") or []
            if not reps:
                break
            for r in reps:
                items.append({
                    "uname": (r.get("member") or {}).get("uname"),
                    "like": r.get("like"),
                    "rcount": r.get("rcount"),
                    "message": (r.get("content") or {}).get("message"),
                })
            page = dd.get("page") or {}
            total = page.get("count", 0)
            print(f"  pn{pn}: {len(reps)} replies (total ~{total})")
            if len(items) >= total or len(reps) < 20:
                break
            time.sleep(1.3)
    except Exception as e:
        print(f"  ERR: {e}")
    all_comments[bv] = {"label": label, "aid": aid, "count": len(items), "comments": items}
    print(f"  -> {len(items)} comments saved")
    time.sleep(2)

with open(os.path.join(OUT, "comments_all.json"), "w", encoding="utf-8") as f:
    json.dump(all_comments, f, ensure_ascii=False, indent=2)
print(f"\n[done] comments saved for {len(all_comments)} videos")
