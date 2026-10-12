# -*- coding: utf-8 -*-
"""
Q002 转火微调 - 加权打分 + 精选
聚焦"转火后的微调定位"，不是泛泛的瞄准教程
"""
import json, re
from pathlib import Path

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q002-转火微调\转火微调-B站原始数据")

data = json.loads((OUT_DIR / "搜索清单.json").read_text(encoding="utf-8"))
videos = data["videos"]

# 主题相关词权重（聚焦"转火后微调"）
POS_KW = [
    # 核心主题词
    ("转火", 8), ("微调", 9), ("定位", 6), ("flick", 7), ("flicking", 7),
    ("target switching", 8), ("targetswitch", 8), ("micro", 6),
    ("微操", 5), ("准星", 3), ("瞄准", 2),
    # 具体场景词
    ("瓦洛兰特", 3), ("valorant", 3), ("kovaak", 4), ("aim lab", 4),
    ("aimlab", 4), ("aim trainer", 4), ("跟枪", 3), ("预瞄", 3),
    ("急停", 2), ("反应", 1), ("肌肉记忆", 2),
    # 问题表现词
    ("转火不准", 6), ("过冲", 4), ("overshoot", 5), ("抖", 2),
    ("修正", 4), ("correction", 5), ("确认感", 4),
    # 训练方法词
    ("训练", 2), ("练习", 1), ("教程", 1), ("技巧", 1), ("进阶", 2),
    ("提升", 1), ("方法", 1), ("怎么练", 3), ("如何", 1),
]

# 负向词（卖课/娱乐/无关）
NEG_KW = [
    ("卖课", -8), ("报名", -6), ("加群", -5), ("vx", -4), ("微信", -3),
    ("抖音", -2), ("快手", -2), ("直播回放", -2),
    ("集锦", -3), ("精彩", -2), ("top", -1), ("名场面", -3),
    ("赛事", -2), ("比赛", -1), ("职业", -1),
    ("轻语", -3), ("苏神", -2),  # 娱乐主播
]

def score(v):
    t = (v.get("title") or "") + " " + (v.get("description") or "")
    tl = t.lower()
    s = 0.0
    for kw, w in POS_KW:
        if kw.lower() in tl:
            s += w
    for kw, w in NEG_KW:
        if kw.lower() in tl:
            s += w
    # 播放量加权
    p = v.get("play") or 0
    if p > 500000: s += 3
    elif p > 100000: s += 2
    elif p > 30000: s += 1
    elif p < 5000: s -= 1
    # 时长：3-20 分钟最有信息量
    d = v.get("_dur_s") or 0
    if d < 60: s -= 2
    elif d < 180: s += 0.5
    elif d < 1200: s += 1.5
    elif d > 3600: s -= 1
    # 多关键词命中加分
    hits = len(v.get("kw_hit", []))
    s += min(hits, 5) * 0.5
    return s

for v in videos:
    v["_score"] = round(score(v), 2)

videos.sort(key=lambda x: -x["_score"])

# 打印 top 60 供人工复核
print(f"Total: {len(videos)} videos\n")
print(f"{'Rk':>3} {'Score':>6} {'Play':>8} {'Dur':>7}  Title")
print("-" * 100)
for i, v in enumerate(videos[:60]):
    play = v.get("play", 0)
    play_s = f"{play/10000:.1f}w" if play >= 10000 else str(play)
    dur = v.get("duration", "")
    print(f"{i+1:>3} {v['_score']:>6.1f} {play_s:>8} {dur:>7}  {v['title'][:50]}  [{v['bvid']}]")

# 落盘评分全量
(OUT_DIR / "评分全量.json").write_text(
    json.dumps(videos, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n[OUT] {(OUT_DIR / '评分全量.json')}")
