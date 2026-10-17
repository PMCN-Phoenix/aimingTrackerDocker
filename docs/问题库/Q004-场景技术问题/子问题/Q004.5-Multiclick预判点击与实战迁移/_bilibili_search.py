# -*- coding: utf-8 -*-
"""B站搜索：Multiclick 120 预判式点击与实战迁移（Q004.5）"""
import sys, json, time, hashlib, urllib.parse, requests, re, os
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

def sign(params):
    cookie = pool.get_cookie()
    s.headers["Cookie"] = cookie
    nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=15).json()
    wbi = nav["data"]["wbi_img"]
    img = wbi["img_url"].rsplit("/",1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/",1)[-1].split(".")[0]
    mixin_key = "".join((img+sub)[i] for i in MIXIN)[:32]
    params["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(params.items()))
    params["w_rid"] = hashlib.md5((q+mixin_key).encode()).hexdigest()
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
    "场景技术": ["multiclick 120", "multiclick kovaak", "kovaak multiclick", "click timing 教学", "点击时机 瞄准", "kovaak 点击 教程"],
    "预瞄迁移": ["无畏契约 预瞄", "瓦罗兰特 预瞄", "valorant 预瞄 教学", "十字准星 摆放", "准星位置 教学", "peek 预瞄 拉枪"],
    "预判与反应": ["瞄准 预判 反应", "预瞄 教学 fps", "定位 丝滑 瞄准", "反应速度 拉枪", "打靶 点击 节奏"],
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
                        "desc": v.get("description", "")[:200],
                        "_kw": [kw],
                        "_group": gname,
                    }
                elif bvid in all_results:
                    if kw not in all_results[bvid]["_kw"]:
                        all_results[bvid]["_kw"].append(kw)
        except Exception as e:
            print(f"  [{kw}] 错误: {e}")
        time.sleep(1.5)

W = [
    ("multiclick", 15), ("预瞄", 14), ("预判", 11), ("click timing", 12), ("点击时机", 11),
    ("准星", 12), ("crosshair placement", 14), ("预判位置", 12),
    ("peek", 8), ("拉枪", 6), ("反应", 6), ("丝滑", 6), ("平滑", 5),
    ("微调", 5), ("定位", 5), ("甩", 4), ("kovaak", 6), ("无畏契约", 6), ("valorant", 6),
    ("瞄准", 3), ("节奏", 4), ("reset", 4), ("复位", 4),
]
def score(v):
    t = ((v["title"] or "") + " " + (v.get("desc") or "")).lower()
    s = sum(w for k, w in W if k.lower() in t)
    if len(v["_kw"]) >= 2: s += 5
    if len(v["_kw"]) >= 3: s += 3
    p = v.get("play") or 0
    s += 4 if p > 100000 else 3 if p > 30000 else 2 if p > 5000 else 1 if p > 1000 else -1
    return s

results = sorted(all_results.values(), key=score, reverse=True)
for i, v in enumerate(results[:30]):
    print(f"  #{i+1} [{score(v)}分] {v['title'][:52]} | {v['author']} | 播放={v['play']} | {v['bvid']}")

out_dir = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q004-场景技术问题\子问题\Q004.5-Multiclick预判点击与实战迁移\B站原始数据"
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "搜索清单.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n总计去重后: {len(results)} 个视频")
print(f"已保存到: {out_dir}\\搜索清单.json")
