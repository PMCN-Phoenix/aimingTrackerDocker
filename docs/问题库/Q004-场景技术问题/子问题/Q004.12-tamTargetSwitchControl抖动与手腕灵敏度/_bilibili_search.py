# -*- coding: utf-8 -*-
"""B站搜索：Q004.12 tamTargetSwitch Control 抖动 / 手腕灵敏度"""
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
    "场景直查": ["tamTargetSwitch", "target switch", "kovaak 切目标",
               "换目标 练习", "多目标 切换 瞄准", "kovaak 转火"],
    "抖动症状": ["鼠标 手抖", "瞄准 手抖", "跟枪 抖", "压枪 手抖",
               "鼠标 抖动 怎么办", "瞄准 不稳 发抖", "手抖 影响瞄准",
               "瞄准 微抖", "鼠标 抖 灵敏度"],
    "手腕控制": ["手腕流 手臂流", "手腕流 瞄准", "手腕 控制 鼠标",
               "握鼠标 姿势", "鼠标 握法 瞄准", "手腕 悬空",
               "鼠标 微调 技巧", "低灵敏度 手腕"],
    "灵敏度参数": ["edpi 多少合适", "灵敏度 太高 不稳", "灵敏度 太低 甩不动",
               "鼠标 dpi 抖动", "回报率 1000hz", "鼠标垫 阻力"],
    "生理机制": ["生理性手抖", "手抖 原因 年轻人", "手抖 紧张",
               "肌肉 张力 瞄准", "放松 瞄准"],
}

os.makedirs("B站原始数据", exist_ok=True)
allv, seen = [], set()
for g, kws in groups.items():
    print(f"\n### {g}")
    for kw in kws:
        try:
            res = search(kw)
        except Exception as e:
            print(f"  [{kw}] ERR {e}")
            continue
        n = 0
        for it in res:
            bv = it.get("bvid")
            if not bv or bv in seen:
                continue
            seen.add(bv)
            play = it.get("play", 0)
            if isinstance(play, str):
                play = 0
            row = {"group": g, "kw": kw, "bvid": bv,
                   "title": re.sub(r"<[^>]+>", "", it.get("title", "")),
                   "author": it.get("author"), "play": play,
                   "duration": it.get("duration"), "aid": it.get("aid")}
            allv.append(row)
            n += 1
        print(f"  [{kw}] +{n}")
        time.sleep(0.6)

allv.sort(key=lambda x: -x["play"])
with open("B站原始数据/搜索清单.json", "w", encoding="utf-8") as f:
    json.dump(allv, f, ensure_ascii=False, indent=2)
print(f"\n共 {len(allv)} 条")
print("\n=== 播放量 Top 25 ===")
for v in allv[:25]:
    print(f"{v['play']:>9} {v['bvid']} {v['duration']:>8} {v['title'][:52]}")
