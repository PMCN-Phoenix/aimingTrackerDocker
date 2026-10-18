# -*- coding: utf-8 -*-
"""B站搜索：技能保持/学了用不出来/状态依赖 + 分数焦虑/成绩心态/探索式学习（Q017）"""
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
    "技能保持痛点": ["练枪 手感 丢失", "练枪 进步 退步", "练枪 学了 用不出来",
               "瞄准 技巧 不稳定", "kovaak 分数 下降", "练枪 分数 波动",
               "手感 是什么 FPS", "练枪 平台期", "肌肉记忆 消失", "技能 遗忘 运动"],
    "分数焦虑心态": ["分数焦虑", "成绩焦虑 游戏", "练枪 心态", "过分关注分数",
               "kovaak 刷分", "aim 分数 焦虑", "打瓦 心态 爆炸", "竞技 心态 调整",
               "太想赢 发挥失常", "choking 游戏", "紧张 发挥失常 电竞", "压力 下 打游戏 手感"],
    "学习与方法论": ["刻意练习 遗忘", "探索 学习 运动", "motor learning 练枪",
               "游戏 学习 方法论", "瞄准 训练 一致性", "pro 状态波动 电竞",
               "aim consistency tips", "练枪 错误 重复", "打瓦 自我怀疑",
               "pressured 练枪 分数"],
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
    ("焦虑", 16), ("心态", 15), ("分数", 14), ("手感", 14), ("退步", 13),
    ("波动", 13), ("紧张", 12), ("压力", 12), ("遗忘", 12), ("肌肉记忆", 12),
    ("平台期", 12), ("不稳定", 11), ("发挥失常", 11), ("状态", 10), ("进步", 10),
    ("焦虑感", 10), ("anxiety", 10), ("choking", 10), ("consistency", 10),
    ("练枪", 9), ("kovaak", 9), ("aim", 8), ("瞄准", 8), ("打瓦", 7),
    ("无畏契约", 6), ("valorant", 6), ("刷分", 8), ("pb", 6), ("benchmark", 6),
    ("刻意练习", 8), ("探索", 7), ("学习", 5), ("职业", 5), ("电竞", 5),
    ("fps", 5), ("fpsa imtrainer", 3), ("训练", 4), ("错误", 5),
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

out_dir = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q017-技能保持与分数焦虑\B站原始数据"
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "搜索清单.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n总计去重后: {len(results)} 个视频")
print(f"已保存到: {out_dir}\\搜索清单.json")
