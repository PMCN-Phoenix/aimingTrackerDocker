# -*- coding: utf-8 -*-
"""B站检索：Q022 跟枪初速度匹配与「加速带」"""
import sys, json, time, hashlib, urllib.parse, requests, re, os
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

def sign(params):
    s.headers["Cookie"] = pool.get_cookie()
    nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=15).json()
    wbi = nav["data"]["wbi_img"]
    img = wbi["img_url"].rsplit("/",1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/",1)[-1].split(".")[0]
    mk = "".join((img+sub)[i] for i in MIXIN)[:32]
    params["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(params.items()))
    params["w_rid"] = hashlib.md5((q+mk).encode()).hexdigest()
    return params

def search(kw, page=1):
    p = sign({"search_type": "video", "keyword": kw, "page": page, "page_size": 30})
    r = s.get("https://api.bilibili.com/x/web-interface/wbi/search/type", params=p, timeout=25).json()
    if r.get("code") != 0:
        print(f"  code={r.get('code')} {r.get('message')}")
        return []
    return r["data"].get("result", [])

groups = {
    "症状与手感": ["跟枪 提前量", "跟枪 预判", "跟枪 跟不上", "跟枪 贴住", "跟枪 速度匹配",
             "匀速跟枪", "跟枪 初速度", "跟枪 起步", "跟枪 甩尾", "跟枪 卡点"],
    "机制": ["平滑跟枪 原理", "跟枪 提前身位", "跟枪 惯性", "鼠标 加速度 跟枪",
           "跟枪 断连", "跟枪 节奏", "跟枪 手眼 协调", "跟枪 视线"],
    "场景与训练": ["psalmTS", "Regen 跟枪", "kovak 跟枪 训练", "voltaic 跟枪",
              "跟枪 训练方法", "平滑跟枪 训练", "反应跟枪", "跟枪 变向"],
}

allr = {}
for g, kws in groups.items():
    print(f"\n=== {g} ===")
    for kw in kws:
        try:
            res = search(kw)
            print(f"  [{kw}] {len(res)}")
            for v in res:
                b = v.get("bvid", "")
                if not b:
                    continue
                if b not in allr:
                    allr[b] = {"bvid": b, "title": re.sub(r"<[^>]+>", "", v.get("title", "")),
                               "author": v.get("author", ""), "play": v.get("play", 0),
                               "duration": v.get("duration", ""), "pubdate": v.get("pubdate", 0),
                               "desc": (v.get("description") or "")[:200],
                               "_kw": [kw], "_group": g}
                elif kw not in allr[b]["_kw"]:
                    allr[b]["_kw"].append(kw)
        except Exception as e:
            print(f"  [{kw}] ERR {e}")
        time.sleep(1.4)

W = [("跟枪", 16), ("平滑", 12), ("提前", 15), ("预判", 13), ("速度", 10), ("匀速", 13),
     ("贴", 10), ("初速", 14), ("加速", 10), ("惯性", 10), ("变向", 10), ("跟踪", 9),
     ("目标", 7), ("鼠标", 7), ("手腕", 6), ("节奏", 9), ("教程", 6), ("教学", 6),
     ("训练", 6), ("瞄准", 7), ("偏差", 9), ("落后", 10), ("丢", 8)]
def score(v):
    t = ((v["title"] or "") + " " + (v.get("desc") or "")).lower()
    sc = sum(w for k, w in W if k in t)
    if len(v["_kw"]) >= 2: sc += 5
    if len(v["_kw"]) >= 3: sc += 3
    p = v.get("play") or 0
    sc += 4 if p > 100000 else 3 if p > 30000 else 2 if p > 5000 else 1 if p > 1000 else -1
    return sc

res = sorted(allr.values(), key=score, reverse=True)
for i, v in enumerate(res[:30]):
    print(f"  #{i+1} [{score(v)}] {v['title'][:50]} | {v['author']} | {v['play']} | {v['bvid']}")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "B站原始数据")
os.makedirs(out, exist_ok=True)
json.dump(res, open(os.path.join(out, "搜索清单.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n去重 {len(res)} 条")
