# -*- coding: utf-8 -*-
"""B站搜索：日常作息/运动/睡眠/疲劳状态对瞄准的影响（Q016 日常作息运动与瞄准状态）"""
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
    "机制痛点": ["打完游戏 手抖", "手抖 瞄准", "手抖 FPS", "跑完步 打游戏 状态",
               "运动后 打游戏", "累了 打游戏 手感", "练枪 状态差", "练枪 手感 消失",
               "瞄准 视野抖动", "疲劳 反应 变慢 游戏"],
    "状态管理": ["电竞 睡眠", "职业选手 作息", "睡眠 反应速度", "状态管理 电竞",
               "电竞 体能训练", "健身 影响 枪法", "运动 电竞 表现", "作息 竞技状态",
               "咖啡因 电竞", "热身 状态 练枪"],
    "英文场景": ["aim 睡眠", "sleep aim training", "aim trainer 疲劳", "esports sleep",
               "hand tremor gaming", "gaming 握力 手抖", "reaction time sleep",
               "flick 变慢 原因"],
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
    ("手抖", 15), ("睡眠", 15), ("熬夜", 14), ("疲劳", 14), ("状态", 13),
    ("反应", 12), ("作息", 12), ("睡眠不足", 12), ("运动", 11), ("健身", 10),
    ("tremor", 10), ("sleep", 10), ("体能", 10), ("手感", 9), ("心率", 9),
    ("电竞", 9), ("练枪", 8), ("瞄准", 8), ("reaction", 8), ("职业", 7),
    ("恢复", 7), ("咖啡因", 6), ("热身", 6), ("颤抖", 6), ("紧张", 5),
    ("打瓦", 5), ("无畏契约", 4), ("valorant", 4), ("FPS", 4), ("kovaak", 4),
    ("aim", 3), ("定位", 3), ("跟枪", 3),
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

out_dir = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q016-日常作息运动与瞄准状态\B站原始数据"
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "搜索清单.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n总计去重后: {len(results)} 个视频")
print(f"已保存到: {out_dir}\\搜索清单.json")
