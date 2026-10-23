# -*- coding: utf-8 -*-
"""B站搜索：随机队友下的舒适打法形态（Q026）

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
    "单排队友应对": [
        "无畏契约 单排 队友", "无畏契约 单排 心态", "单排 遇到 摆烂 队友",
        "单排 路人 怎么打", "无畏契约 单排 上分 技巧", "单排 队友 不沟通",
        "无畏契约 单排 避坑", "单排 队友 送 怎么办", "无畏契约 一个人 打排位",
    ],
    "打法风格与自我定位": [
        "无畏契约 打法 风格", "找到 自己 的 打法", "无畏契约 英雄池",
        "单排 玩什么 英雄", "无畏契约 专精 一个 英雄", "无畏契约 补位 还是 专精",
        "无畏契约 适合 玩 什么 位置", "无畏契约 打法 定型",
    ],
    "单排与车队对比": [
        "单排 双排 区别", "无畏契约 单排 五排", "单排 上分 难",
        "车队 单排 差距", "无畏契约 组排 单排 哪个好", "单排 练不到 东西",
    ],
    "决策与节奏（单人可控）": [
        "无畏契约 节奏 掌控", "无畏契约 默认 打法", "无畏契约 default 战术",
        "无畏契约 控图", "无畏契约 决策", "无畏契约 信息 判断",
        "无畏契约 单排 指挥", "无畏契约 回合 思路",
    ],
    "心态与情绪管理": [
        "无畏契约 排位 心态", "无畏契约 连败", "无畏契约 上头 连跪",
        "打游戏 情绪 管理", "无畏契约 心态 崩", "排位 焦虑",
    ],
    "舒适区与固化（反方）": [
        "舒适区 游戏", "打法 固化", "一直 单排 缺点", "英雄池 太浅",
        "打游戏 舒适区", "无畏契约 坏习惯",
    ],
    "职业/教练视角": [
        "职业选手 单排", "无畏契约 教练 单排", "无畏契约 提高 意识",
        "无畏契约 上分 教学 单排", "无畏契约 思路 教学",
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
    ("单排", 16), ("路人", 15), ("队友", 14), ("排位", 10), ("上分", 11),
    ("心态", 13), ("打法", 13), ("风格", 11), ("英雄池", 12), ("专精", 10),
    ("补位", 10), ("选角", 10), ("适合", 9), ("舒适", 12), ("固化", 9),
    ("节奏", 9), ("决策", 10), ("默认", 8), ("控图", 8), ("意识", 9),
    ("沟通", 9), ("开麦", 9), ("指挥", 8), ("连败", 10), ("情绪", 9),
    ("教学", 7), ("教练", 9), ("职业", 7), ("避坑", 9), ("误区", 9),
    ("为什么", 6), ("怎么", 5), ("无畏契约", 6), ("瓦罗兰特", 6), ("瓦", 3),
]
NEG = [("集锦", 8), ("搞笑", 8), ("高光", 8), ("剪辑", 6), ("整活", 8),
       ("皮肤", 6), ("版本更新", 4), ("新手入门", 3)]

def score(v):
    t = ((v["title"] or "") + " " + (v.get("desc") or "")).lower()
    sc = sum(w for k, w in W if k.lower() in t)
    sc -= sum(w for k, w in NEG if k.lower() in t)
    nkw = len(v["_kw"]); ngrp = len(v["_group"])
    if nkw >= 2: sc += 6
    if nkw >= 3: sc += 4
    if ngrp >= 2: sc += 5
    p = v.get("play") or 0
    sc += 4 if p > 200000 else 3 if p > 50000 else 2 if p > 10000 else 1 if p > 2000 else -1
    return sc

results = sorted(all_results.values(), key=score, reverse=True)
for i, v in enumerate(results[:40]):
    print(f"  #{i+1} [{score(v)}分] {v['title'][:50]} | {v['author']} | 播放={v['play']} | {v['bvid']}")

out_dir = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q026-随机队友下的舒适打法形态\B站原始数据"
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "搜索清单.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n总计去重后: {len(results)} 个视频")
print(f"分组覆盖: {groups.keys()}")
print(f"已保存: {out_dir}\\搜索清单.json")
