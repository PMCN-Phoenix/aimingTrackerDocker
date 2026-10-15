# -*- coding: utf-8 -*-
"""Step2: 去重+打分, 精选 12-15 个视频, 输出 shortlist.json"""
import json, os, re

OUT = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q011-跑步速度心率关系\B站原始数据"

with open(os.path.join(OUT, "search_raw.json"), "r", encoding="utf-8") as f:
    raw = json.load(f)

# 去重合并
bv_map = {}
for kw, items in raw.items():
    for it in items:
        bv = it["bvid"]
        if not bv:
            continue
        if bv not in bv_map:
            bv_map[bv] = dict(it)
            bv_map[bv]["_hit_kws"] = []
            bv_map[bv]["_kw_count"] = 0
        bv_map[bv]["_hit_kws"].append(kw)
        bv_map[bv]["_kw_count"] += 1

# duration 是 "mm:ss" 或 "hh:mm:ss"
def dur_to_sec(d):
    if not d: return 0
    parts = str(d).split(":")
    try:
        parts = [int(x) for x in parts]
    except:
        return 0
    if len(parts) == 2:
        return parts[0]*60 + parts[1]
    if len(parts) == 3:
        return parts[0]*3600 + parts[1]*60 + parts[2]
    return 0

# 专业 UP 主关键词（跑步/运动领域常见账号）
PRO_AUTHOR_HINTS = ["跑步", "跑", "马拉松", "田径", "体能", "训练", "运动", "fitness", "run",
                    "Jeff", "jeff", "斌", "马拉松", "越野", "耐力", "cycling", "骑行"]

# 主题相关关键词权重
KW_WEIGHTS = [
    # 方向1 基础关系
    ("心率", 2.0), ("配速", 2.0), ("心率区间", 4.0), ("最大心率", 2.5), ("静息心率", 2.5),
    # 方向2 长时间有氧
    ("有氧", 3.0), ("Z2", 3.5), ("马拉松", 2.5), ("心率漂移", 4.0), ("长距离", 2.0), ("慢跑", 1.5),
    # 方向3 短时间+方法
    ("间歇", 3.5), ("乳酸阈值", 4.0), ("VO2max", 3.5), ("VDOT", 4.0), ("乳酸", 3.0),
    ("阈值", 3.0), ("冲刺", 2.0), ("高强度", 1.5),
    # 通用方法
    ("训练", 1.0), ("教学", 1.0), ("科普", 1.0), ("公式", 1.5), ("换算", 2.0),
    ("储备心率", 3.0), ("RPE", 2.0), ("主观", 0.5),
    # 反面/争议
    ("不准", 1.5), ("坑", 1.0), ("误区", 1.5), ("错误", 1.0), ("别再", 1.0),
]

def score(v):
    t = ((v.get("title") or "") + " " + (v.get("description") or "")).lower()
    s = 0.0
    for k, w in KW_WEIGHTS:
        if k.lower() in t:
            s += w
    # 播放量
    play = v.get("play") or 0
    if play > 500000: s += 4
    elif play > 200000: s += 3
    elif play > 50000: s += 2
    elif play > 10000: s += 1
    elif play > 3000: s += 0
    else: s -= 1
    # 弹幕量
    dm = v.get("danmaku") or 0
    if dm > 500: s += 1.5
    elif dm > 100: s += 0.8
    # 命中多关键词加分
    s += v["_kw_count"] * 1.5
    # 时长：3-30 分钟信息量最佳
    dur = dur_to_sec(v.get("duration"))
    v["_dur_s"] = dur
    if dur < 90: s -= 2          # 太短
    elif dur > 3600: s -= 1.5    # 太长（直播/录屏）
    elif dur < 180: s -= 0.5
    # 标题里出现"教程/教学/详解/原理/为什么"加分
    for k in ["原理", "详解", "为什么", "公式", "怎么算", "如何", "实测", "数据"]:
        if k in (v.get("title") or ""):
            s += 0.8
    # UP 主专业度粗判
    author = v.get("author") or ""
    for k in PRO_AUTHOR_HINTS:
        if k.lower() in author.lower():
            s += 0.5
            break
    # 排除明显不相关（标题完全没心率/跑相关词）
    title = v.get("title") or ""
    if not any(k in title for k in ["心率", "配速", "跑", "有氧", "乳酸", "VDOT", "Z2", "训练"]):
        s -= 5
    return s

scored = []
for bv, v in bv_map.items():
    v2 = dict(v)
    v2["score"] = score(v)
    v2["bvid"] = bv
    scored.append(v2)

scored.sort(key=lambda x: -x["score"])

# 打印 top 40 人工过目
print(f"Total unique: {len(scored)}\n")
print(f"{'score':>6} {'play':>8} {'dur':>8} {'kws':>3}  title / author")
for i, v in enumerate(scored[:40]):
    play = v.get("play") or 0
    print(f"{v['score']:6.1f} {play:8d} {str(v.get('duration')):>8} {v['_kw_count']:3d}  {v['title'][:50]} | {v.get('author','')[:20]}")

# 落盘 top 80 供人工挑
out = os.path.join(OUT, "scored_top.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(scored[:80], f, ensure_ascii=False, indent=2)
print(f"\n[saved] top80 -> {out}")
