# -*- coding: utf-8 -*-
"""B站搜索：周期训练乏味与实战冲刷（Q027）

分组原则（SOP 第一节）：按「主题方向」分组，不是堆近义词。
每组代表一个独立的答案来源，组内关键词才是同方向的不同说法。
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
    "训练枯燥的直接现象": [
        "练枪 枯燥", "练枪 无聊", "练枪 练不下去", "每天练枪 坚持不下去",
        "aimlab 枯燥", "kovaak 无聊", "练枪 厌倦", "练枪 有意思吗",
        "练枪 好累", "长期 练枪 心态",
    ],
    "训练倦怠与心理疲劳": [
        "训练 倦怠", "心理疲劳 训练", "过度训练 症状", "运动 倦怠 恢复",
        "训练 疲劳 心理", "burnout 训练", "训练 厌倦期", "竞技 倦怠",
        "训练 动机 下降", "丧失 训练 兴趣",
    ],
    "训练安排与周期化": [
        "训练 周期 安排", "周期化 训练", "训练 计划 变化", "每天 练 一样",
        "训练 单调", "训练 内容 变化", "游戏 训练 计划", "训练 强度 安排",
        "训练 恢复 日", "训练 分化",
    ],
    "实战与训练的关系": [
        "练枪 实战 区别", "靶场 实战 差距", "死斗 练枪", "练枪 转化 实战",
        "训练 为了 实战", "练枪 没用 实战", "aimlab 实战 差距",
        "训练 检验 实战", "实战 才是 检验",
    ],
    "动机与奖赏机制": [
        "打游戏 动机", "为什么 打游戏", "上分 动力", "游戏 成就感",
        "游戏 即时反馈", "延迟满足 游戏", "游戏 多巴胺", "正反馈 游戏",
        "打游戏 意义", "训练 目标 设定",
    ],
    "习惯与坚持（行为设计）": [
        "坚持 训练 方法", "习惯 养成 游戏", "每天 练枪 习惯",
        "如何 坚持 练习", "训练 自律", "习惯 打卡 训练",
        "练习 上瘾 机制", "让 练习 有趣",
    ],
    "反方与误区": [
        "练得越多 越好 吗", "不练 会 掉 吗", "靠意志力 坚持",
        "把 爱好 变成 工作", "游戏 变成 负担", "电竞 训练 痛苦",
        "职业选手 训练 枯燥", "过度练习 反效果",
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

# 打分权重：针对本主题重写（不是通用热度排序）
W = [
    ("枯燥", 18), ("乏味", 18), ("无聊", 15), ("厌倦", 16), ("倦怠", 18),
    ("坚持", 13), ("动力", 14), ("动机", 14), ("单调", 15), ("疲劳", 12),
    ("周期", 11), ("变化", 11), ("新鲜", 12), ("兴趣", 11), ("热爱", 10),
    ("习惯", 11), ("实战", 12), ("转化", 10), ("反馈", 11), ("成就", 9),
    ("意义", 9), ("恢复", 9), ("休息", 8), ("休息日", 10), ("心态", 8),
    ("训练", 6), ("练枪", 8), ("练习", 6), ("游戏", 3), ("为什么", 5),
    ("方法", 5), ("误区", 9), ("反效果", 10), ("过度", 9),
]
NEG = [("集锦", 10), ("搞笑", 10), ("高光", 9), ("整活", 10), ("皮肤", 6),
       ("版本更新", 5), ("赛事回放", 8), ("比赛录像", 6), ("萌新", 3)]

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

out_dir = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q027-周期训练乏味与实战冲刷\B站原始数据"
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "搜索清单.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n总计去重后: {len(results)} 个视频")
print(f"已保存: {out_dir}\\搜索清单.json")
