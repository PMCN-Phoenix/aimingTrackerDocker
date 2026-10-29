# -*- coding: utf-8 -*-
"""B站搜索：练了就能长吗？限制条件是什么？（Q029）

分组原则（SOP 第一节）：按「主题方向」分组，不是堆近义词。
"""
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
    if r.status_code == 412 or '"code":-412' in r.text:
        pool.report_412()
        print("    412 风控，切换账号")
        return []
    pool.report_success()
    res = r.json()
    if res.get("code") != 0:
        print(f"    code={res.get('code')} msg={res.get('message')}")
        return []
    return res["data"].get("result", [])

groups = {
    "练了没进步的直接现象": [
        "练枪 没进步", "练枪 没提升", "练枪 分数不涨", "练枪 为什么 没用",
        "aimlab 没进步", "kovaak 没提升", "每天练枪 没变强", "练枪 白练",
        "练枪 越练越菜", "练枪 停滞",
    ],
    "平台期与瓶颈": [
        "练枪 瓶颈期", "枪法 瓶颈", "游戏 平台期", "aim 瓶颈 突破",
        "卡段 瓶颈", "瓶颈期 怎么突破", "枪法 停滞 不涨", "分数 平台期",
        "练习 瓶颈 原因", "突破 枪法 极限",
    ],
    "练法质量（数量≠质量）": [
        "刻意练习", "正确 练枪 方法", "练枪 方法 错误", "盲目 练枪",
        "有效 练习", "练习 质量 数量", "怎么 练枪 才 有用", "科学 练枪",
        "练枪 姿势 细节", "针对性 训练 弱点",
    ],
    "难度与场景选择": [
        "练枪 场景 选择", "aim 场景 难度", "voltaic 场景 推人选", "练枪 难度 太高",
        "练枪 难度 合适", "kovaak 场景 怎么选", "从 简单 开始 练", "跳级 难度 练习",
    ],
    "天赋与极限": [
        "枪法 天赋", "FPS 天赋 重要 吗", "努力 天赋 游戏", "天赋 决定 上限",
        "反应速度 天赋", "天赋 训练 上限", "普通玩家 上限", "手速 天赋",
    ],
    "身体条件与状态": [
        "睡眠 训练 效果", "睡眠 技能 巩固", "状态 差 练枪", "休息 练习 效果",
        "疲劳 练习 无效", "专注力 练习", "练枪 手感 状态",
    ],
    "迁移与专项性": [
        "练枪 实战 迁移", "训练 专项性", "练枪 不如 死斗", "练习 泛化",
        "枪法 一致性 稳定", "练枪 巩固 遗忘",
    ],
    "反方与误区（多练≠一定好）": [
        "练得 多 一定 好 吗", "无效 练习", "自我感动 练习", "练习 边际 递减",
        "过度练习", "肌肉记忆 误区", "手感 迷信",
    ],
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
                if not bvid:
                    continue
                title = re.sub(r"<[^>]+>", "", v.get("title", ""))
                if bvid not in all_results:
                    all_results[bvid] = {
                        "bvid": bvid,
                        "title": title,
                        "author": v.get("author", ""),
                        "play": v.get("play", 0),
                        "duration": v.get("duration", ""),
                        "pubdate": v.get("pubdate", 0),
                        "desc": (v.get("description") or "")[:220],
                        "_kw": [kw],
                        "_group": [gname],
                    }
                else:
                    if kw not in all_results[bvid]["_kw"]:
                        all_results[bvid]["_kw"].append(kw)
                    if gname not in all_results[bvid]["_group"]:
                        all_results[bvid]["_group"].append(gname)
        except Exception as e:
            print(f"  [{kw}] 错误: {e}")
        time.sleep(1.4)

# 打分权重：针对本主题重写
W = [
    ("没进步", 20), ("没提升", 20), ("没用", 16), ("白练", 18), ("不涨", 16),
    ("瓶颈", 20), ("平台期", 18), ("停滞", 16), ("卡", 8),
    ("天赋", 16), ("极限", 12), ("上限", 12),
    ("方法", 12), ("错误", 12), ("误区", 14), ("正确", 10), ("科学", 10),
    ("刻意", 14), ("质量", 12), ("有效", 12), ("无效", 14), ("自我感动", 15),
    ("难度", 12), ("场景", 8), ("合适", 8), ("挑战", 8),
    ("睡眠", 12), ("状态", 10), ("休息", 8), ("专注", 9), ("疲劳", 9),
    ("肌肉记忆", 12), ("手感", 9), ("遗忘", 9), ("巩固", 9), ("专项", 10),
    ("练枪", 8), ("练习", 7), ("训练", 6), ("aim", 7), ("为什么", 6), ("边际", 12),
]
NEG = [("集锦", 10), ("搞笑", 10), ("高光", 9), ("整活", 10), ("皮肤", 6),
       ("赛事回放", 8), ("比赛录像", 6), ("原神", 12), ("王者荣耀", 12),
       ("LOL", 10), ("英雄联盟", 10), ("CSGO", 5), ("cs2", 5)]

def score(v):
    t = ((v["title"] or "") + " " + (v.get("desc") or "")).lower()
    sc = sum(w for k, w in W if k.lower() in t)
    sc -= sum(w for k, w in NEG if k.lower() in t)
    nkw = len(v["_kw"]); ngrp = len(v["_group"])
    if nkw >= 2: sc += 6
    if nkw >= 3: sc += 4
    if ngrp >= 2: sc += 6
    p = v.get("play") or 0
    sc += 4 if p > 200000 else 3 if p > 50000 else 2 if p > 10000 else 1 if p > 2000 else -1
    return sc

results = sorted(all_results.values(), key=score, reverse=True)
for i, v in enumerate(results[:45]):
    print(f"  #{i+1} [{score(v)}分] {v['title'][:52]} | {v['author']} | 播放={v['play']} | {v['bvid']}")

out_dir = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q029-练了就能长吗与限制条件\B站原始数据"
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "搜索清单.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n总计去重后: {len(results)} 个视频")
print(f"已保存: {out_dir}\\搜索清单.json")
