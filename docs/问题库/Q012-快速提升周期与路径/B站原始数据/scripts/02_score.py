# -*- coding: utf-8 -*-
"""
Q012 B站调研 - 第2步：加权打分精选12-15个视频
打分：播放量(0.3) + 互动率(0.2) + 标题相关度(0.3) + UP主专业性(0.2)
输出：精选列表.json
"""
import json, re
from pathlib import Path

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q012-快速提升周期与路径\B站原始数据")

# 相关度关键词权重（标题+描述）
RELEVANCE_KW = [
    # 主题A：周期
    ("多久", 5), ("多长时间", 5), ("周期", 5), ("几周", 4), ("几个月", 4),
    ("几天", 3), ("多久能", 4), ("上辐能", 4), ("上超凡", 4), ("上钻石", 3),
    ("从", 1), ("到", 1),
    # 主题B：方法/效率
    ("快速提升", 5), ("提升方法", 5), ("上分", 3), ("训练计划", 5),
    ("效率", 3), ("瓶颈", 4), ("卡段", 4), ("突破", 3), ("技巧", 2),
    ("教学", 2), ("攻略", 2),
    # 主题C：意识/复盘/结构
    ("复盘", 4), ("意识", 4), ("大局观", 5), ("战术", 3), ("思路", 3),
    ("每天", 4), ("安排", 3), ("时间分配", 5), ("练枪", 2),
    # 排除词（降低相关度）
    ("集锦", -3), ("剪辑", -2), ("搞笑", -4), ("欢乐", -3),
    ("录屏", -1), ("第一视角", -1), (" montage", -2),
]

# UP主专业性信号（作者名或描述里出现）
PROF_KW = [
    ("教练", 5), ("职业", 4), ("前职业", 4), ("青训", 3),
    ("辐能", 4), ("赋能", 4), ("超凡", 3), ("不朽", 2),
    ("数据分析", 3), ("指南", 2), ("干货", 2), ("教学", 2),
]


def dur_sec(s):
    try:
        if ":" in s:
            parts = s.split(":")
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except Exception:
        pass
    return 0


def norm_play(p):
    """播放量归一化到0-1（log尺度，参考10万播放=0.5，100万=0.85）"""
    import math
    if p <= 0:
        return 0
    # log10: 1000=3, 1万=4, 10万=5, 100万=6, 1000万=7
    x = math.log10(p)
    return max(0, min(1, (x - 3) / 4))


def norm_engagement(v):
    """互动率：(favorites+reply+danmaku)/play"""
    play = v.get("play", 0) or 0
    if play <= 0:
        return 0
    eng = (v.get("favorites", 0) + v.get("reply", 0) + v.get("danmaku", 0)) / play
    # 正常互动率0.01-0.05，归一化
    return max(0, min(1, eng / 0.05))


def relevance_score(v):
    text = (v.get("title", "") + " " + v.get("description", "")).lower()
    s = 0
    for kw, w in RELEVANCE_KW:
        if kw.lower() in text:
            s += w
    return max(0, min(1, s / 15))


def pro_score(v):
    text = (v.get("author", "") + " " + v.get("description", "") + " " + v.get("title", "")).lower()
    s = 0
    for kw, w in PROF_KW:
        if kw.lower() in text:
            s += w
    # 时长加分：5-30分钟的干货视频比短视频更有料
    d = dur_sec(v.get("duration", ""))
    if 300 <= d <= 2400:
        s += 3
    elif d > 2400:
        s += 2
    elif d < 120:
        s -= 3
    return max(0, min(1, s / 10))


def main():
    data = json.load(open(OUT_DIR / "搜索结果.json", encoding="utf-8"))
    vs = data["videos"]
    print(f"待打分: {len(vs)}")

    scored = []
    for v in vs:
        s_play = norm_play(v.get("play", 0))
        s_eng = norm_engagement(v)
        s_rel = relevance_score(v)
        s_pro = pro_score(v)
        total = s_play * 0.3 + s_eng * 0.2 + s_rel * 0.3 + s_pro * 0.2
        v["_score"] = {
            "play": round(s_play, 3),
            "engagement": round(s_eng, 3),
            "relevance": round(s_rel, 3),
            "pro": round(s_pro, 3),
            "total": round(total, 3),
        }
        scored.append(v)

    scored.sort(key=lambda x: -x["_score"]["total"])

    # 打印top40供人工判断
    print("\n=== TOP 40 ===")
    for i, v in enumerate(scored[:40]):
        s = v["_score"]
        print(f"{i+1:2}. [{s['total']:.2f}] play={v.get('play',0):>7} dur={v.get('duration',''):>7} "
              f"| {v['bvid']} | {v['title'][:42]} | {v['author']}")

    # 自动选前15，但需要人工审核后再调整
    selected = scored[:15]
    out = {
        "select_time": __import__("time").strftime("%Y-%m-%d %H:%M:%S"),
        "rule": "播放量0.3+互动率0.2+相关度0.3+UP主专业性0.2",
        "selected": [],
    }
    for v in selected:
        out["selected"].append({
            "bvid": v["bvid"],
            "title": v["title"],
            "author": v["author"],
            "mid": v.get("mid", 0),
            "play": v.get("play", 0),
            "favorites": v.get("favorites", 0),
            "reply": v.get("reply", 0),
            "danmaku": v.get("danmaku", 0),
            "duration": v.get("duration", ""),
            "pubdate": v.get("pubdate", 0),
            "description": v.get("description", ""),
            "hit_themes": v.get("hit_themes", [v.get("keyword_hit")]),
            "hit_keywords": v.get("hit_keywords", [v.get("source_keyword")]),
            "score": v["_score"],
            "入选理由": f"相关度{v['_score']['relevance']:.2f}/播放{v['_score']['play']:.2f}/专业度{v['_score']['pro']:.2f}",
        })

    (OUT_DIR / "精选列表.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已保存精选列表.json: {len(selected)} 个视频")


if __name__ == "__main__":
    main()
