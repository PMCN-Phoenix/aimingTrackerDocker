# -*- coding: utf-8 -*-
"""B站检索：Q024 练枪怎么迁移到实战 + 实战紧张（肌肉紧/思路紧/发挥不出来）"""
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
    "症状：练了用不出来": ["练枪 实战 没用", "练枪 打不出来", "练枪 白练", "靶场 猛 实战 菜",
                   "aimlab 实战", "练枪 和 实战 差距", "练枪 多久 见效 实战", "死斗 练枪",
                   "练枪 分数 高 实战 差", "实战 发挥不出来"],
    "症状：紧张与肌肉": ["实战 紧张", "排位 紧张 手抖", "比赛 紧张 手抖", "打游戏 手僵",
                  "紧张 手抖 怎么办", "FPS 紧张", "对枪 紧张", "残局 紧张",
                  "打游戏 心跳 加速", "紧张 肌肉 僵硬"],
    "机制：为什么会紧": ["心理素质 电竞", "比赛 心态", "过度思考 动作", "意识 破坏 本能",
                  "紧张 肌肉 紧张 原理", "交感神经 紧张", "竞技 焦虑", "压力 表现",
                  "心流 游戏", "自动 执行 技能"],
    "方法：迁移与调节": ["实战 迁移 训练", "模拟 实战 训练", "无畏契约 训练 方法",
                  "如何 冷静 打游戏", "呼吸 放松 比赛", "赛前 热身 游戏",
                  "心理 训练 电竞", "脱敏 训练 比赛", "以赛代练", "实战 心态 调整"],
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

W = [("实战", 16), ("紧张", 16), ("迁移", 15), ("发挥", 14), ("心态", 13), ("心理", 13),
     ("僵硬", 14), ("手抖", 14), ("压力", 12), ("焦虑", 12), ("比赛", 11), ("排位", 10),
     ("练枪", 10), ("靶场", 9), ("肌肉", 10), ("放松", 10), ("呼吸", 9), ("冷静", 11),
     ("白练", 13), ("用不出来", 14), ("差距", 9), ("死斗", 8), ("训练", 7), ("瞄准", 7),
     ("教学", 5), ("教程", 5), ("电竞", 8), ("职业", 6)]

def score(v):
    t = ((v["title"] or "") + " " + (v.get("desc") or "")).lower()
    sc = sum(w for k, w in W if k in t)
    if len(v["_kw"]) >= 2: sc += 5
    if len(v["_kw"]) >= 3: sc += 3
    p = v.get("play") or 0
    sc += 4 if p > 100000 else 3 if p > 30000 else 2 if p > 5000 else 1 if p > 1000 else -1
    return sc

res = sorted(allr.values(), key=score, reverse=True)
for i, v in enumerate(res[:40]):
    print(f"  #{i+1} [{score(v)}] {v['title'][:52]} | {v['author']} | {v['play']} | {v['bvid']}")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "B站原始数据")
os.makedirs(out, exist_ok=True)
json.dump(res, open(os.path.join(out, "搜索清单.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n去重 {len(res)} 条")
