# -*- coding: utf-8 -*-
"""B站搜索：Q004.11 Smooth Thin Strafes —— 变向时眼睛反应不过来"""
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
    img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
    mixin_key = "".join((img + sub)[i] for i in MIXIN)[:32]
    params["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(params.items()))
    params["w_rid"] = hashlib.md5((q + mixin_key).encode()).hexdigest()
    return params

def search(kw, page=1):
    p = sign({"search_type": "video", "keyword": kw, "page": page, "page_size": 30})
    r = s.get("https://api.bilibili.com/x/web-interface/wbi/search/type", params=p, timeout=25)
    res = r.json()
    if res.get("code") != 0:
        print(f"  code={res.get('code')} msg={res.get('message')}")
        return []
    return res["data"].get("result", [])

groups = {
    "场景直查": ["smooth thin strafes", "thin strafes", "kovaak 变向",
               "平滑跟枪 变向", "变向 跟枪 教学", "kovaak 反应跟枪"],
    "视觉机制": ["跟枪 眼睛 看哪里", "瞄准 看目标 还是 准星", "动态视力 训练",
               "余光 瞄准", "周边视觉 瞄准", "眼睛 跟不上 目标",
               "瞄准 眼睛 累", "视觉 反应 瞄准"],
    "变向痛点": ["变向 反应不过来", "目标 变向 看不清", "变向 跟不上",
               "跟枪 卡顿", "跟枪 变向 甩飞", "高速 变向"],
    "细目标": ["细目标 瞄准", "小目标 跟枪", "细杆 目标", "目标太小 跟不住"],
}

all_results = {}
for gname, keywords in groups.items():
    print(f"\n=== 分组: {gname} ===")
    for kw in keywords:
        try:
            res = search(kw)
            print(f"  [{kw}] {len(res)}条")
            for v in res:
                bvid = v.get("bvid", "")
                if bvid and bvid not in all_results:
                    title = re.sub(r"<[^>]+>", "", v.get("title", ""))
                    all_results[bvid] = {
                        "bvid": bvid,
                        "title": title,
                        "author": v.get("author", ""),
                        "play": v.get("play", 0),
                        "duration": v.get("duration", ""),
                        "pubdate": v.get("pubdate", 0),
                        "desc": re.sub(r"<[^>]+>", "", v.get("description", "")),
                        "group": gname,
                        "keyword": kw,
                    }
        except Exception as e:
            print(f"  ERR [{kw}] {e}")
        time.sleep(0.8)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "B站原始数据", "搜索清单.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(all_results, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(f"\n去重后 {len(all_results)} 个视频 -> {out}")
top = sorted(all_results.values(), key=lambda x: -x["play"])[:25]
for v in top:
    print(f"  {v['play']:>8} | {v['bvid']} | {v['title'][:52]}")
