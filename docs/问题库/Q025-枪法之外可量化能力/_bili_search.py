# -*- coding: utf-8 -*-
"""B站搜索：枪法之外可练可量化的能力（Q025 v2）

分组原则（SOP 第一节）：按「主题方向」分组，不是堆近义词。
每组代表一个独立的答案来源（= 一类能力 / 一类反方意见），组内关键词才是同方向的不同说法。
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
    "急停与停射纪律": [
        "无畏契约 急停 教学", "无畏契约 急停 怎么练", "无畏契约 反向急停",
        "瓦罗兰特 急停 练习", "无畏契约 停射", "无畏契约 移动 开枪 站定",
    ],
    "预瞄与爆头线": [
        "无畏契约 预瞄 教学", "无畏契约 爆头线", "无畏契约 准星 高度",
        "无畏契约 预瞄 练习方法", "无畏契约 爆头率 提高", "无畏契约 准星放置",
    ],
    "Peek 与身法": [
        "无畏契约 peek 教学", "无畏契约 jiggle peek", "无畏契约 干拉",
        "无畏契约 身法 教学", "无畏契约 大拉 小拉", "无畏契约 静步 走位",
    ],
    "道具与点位": [
        "无畏契约 点位 教学", "无畏契约 lineup 教学", "无畏契约 道具 练习",
        "无畏契约 烟位 教学", "无畏契约 闪光 使用", "无畏契约 技能 组合",
    ],
    "信息意识与决策": [
        "无畏契约 意识 教学", "无畏契约 小地图 信息", "无畏契约 大局观",
        "无畏契约 决策 思路", "无畏契约 信息 判断", "无畏契约 局面 判断",
    ],
    "经济与团队节奏": [
        "无畏契约 经济 教学", "无畏契约 半买 eco", "无畏契约 经济 管理",
        "无畏契约 回合 节奏", "无畏契约 团队 配合", "无畏契约 残局 处理",
    ],
    "复盘与训练方法": [
        "无畏契约 复盘 方法", "无畏契约 训练 计划", "无畏契约 怎么 提高",
        "无畏契约 练枪 多久", "无畏契约 死斗 练习", "无畏契约 训练场 练习",
    ],
    "数据与量化指标": [
        "无畏契约 tracker 数据", "无畏契约 数据 分析", "valorant 战绩 怎么看",
        "无畏契约 kast 含义", "无畏契约 acs 含义", "无畏契约 数据 提升",
    ],
    "心态与专注": [
        "无畏契约 心态 教学", "无畏契约 紧张 手抖", "无畏契约 排位 焦虑",
        "无畏契约 专注力", "无畏契约 心理 素质", "无畏契约 连败 心态",
    ],
    "反方与误区（练枪无用/只练枪）": [
        "无畏契约 练枪 没用", "无畏契约 枪法 误区", "aimlab 有用吗",
        "kovaak 有用吗", "无畏契约 只练枪", "无畏契约 上分 误区",
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

# 打分权重：针对「枪法之外的可练能力」重写
W = [
    ("急停", 15), ("停射", 14), ("预瞄", 15), ("爆头线", 14), ("准星", 12),
    ("peek", 13), ("身法", 13), ("拉枪", 10), ("静步", 9), ("干拉", 10),
    ("道具", 12), ("点位", 12), ("lineup", 10), ("烟", 8), ("闪光", 9),
    ("意识", 14), ("信息", 11), ("决策", 12), ("大局观", 12), ("判断", 9),
    ("经济", 12), ("eco", 9), ("半买", 10), ("残局", 10), ("节奏", 9),
    ("复盘", 14), ("训练", 10), ("练习", 9), ("方法", 8), ("提高", 9),
    ("数据", 10), ("指标", 9), ("量化", 12), ("tracker", 9), ("acs", 7), ("kast", 8),
    ("心态", 10), ("心理", 10), ("专注", 10), ("焦虑", 9), ("紧张", 9),
    ("误区", 10), ("没用", 8), ("教学", 7), ("怎么练", 10), ("多久", 6),
    ("无畏契约", 6), ("瓦罗兰特", 6), ("瓦", 3),
]
NEG = [("集锦", 9), ("搞笑", 9), ("高光", 9), ("剪辑", 7), ("整活", 9),
       ("皮肤", 7), ("剧情", 6), ("赛事", 4), ("比赛回放", 4), ("新手入门", 3),
       ("手机", 6), ("手游", 8), ("动画", 6)]

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
for i, v in enumerate(results[:50]):
    print(f"  #{i+1} [{score(v)}分] {v['title'][:52]} | {v['author']} | 播放={v['play']} | {v['bvid']}")

out_dir = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q025-枪法之外可量化能力\B站原始数据"
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "搜索清单.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n总计去重后: {len(results)} 个视频")
print(f"关键词总数: {sum(len(v) for v in groups.values())}  分组数: {len(groups)}")
print(f"已保存: {out_dir}\\搜索清单.json")
