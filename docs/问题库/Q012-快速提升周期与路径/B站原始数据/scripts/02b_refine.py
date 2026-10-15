# -*- coding: utf-8 -*-
"""
Q012 B站调研 - 第2步b：人工精选15个视频（覆盖三主题）
排除：手游、纯练枪(与Q009重叠)、过短(<3min)、标题党
"""
import json, time
from pathlib import Path

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q012-快速提升周期与路径\B站原始数据")

# 人工精选bvid列表（15个，覆盖三主题）
PICK = [
    # === 主题A：周期/时间（5个）===
    ("BV12Egyz5EXy", "A", "一个黄金白金要多久上超凡？一个月足够了——直接给周期数字"),
    ("BV12SxVeTEGX", "A", "一年黄金到赋能的练枪路径——长周期真实案例"),
    ("BV1cL411Q7id", "A", "40岁白银上钻石——跨年龄周期案例"),
    ("BV1ga37zyETR", "A", "300小时打上超凡——投入产出量化"),
    ("BV1a2VB6aE1T", "A", "从黑铁三到赋能全历程——段位阶梯周期"),
    # === 主题B：快速提升方法/瓶颈（6个）===
    ("BV1tButzYE8d", "B", "赋能3分钟教练枪，两周脱离下三段——核心方法+周期"),
    ("BV19XzHYsEdy", "B", "上超凡做好这几点——突破瓶颈清单(第七期，系列化)"),
    ("BV1konPzpEjc", "B", "卡黄金铂金怎么突破——中段位瓶颈诊断"),
    ("BV1W4HTzeELF", "B", "枪法好但赢不了？意识底层逻辑——前游戏策划视角"),
    ("BV11A376WEv2", "B", "想进步但不知道哪里有问题——自我诊断框架"),
    ("BV1pdVozEEbS", "B", "各段位典型问题总结(复盘上百水友)——段位差异"),
    # === 主题C：复盘/意识/训练结构（4个）===
    ("BV1tyF7zjE5v", "C", "高效自我复盘方法——区别于看Demo"),
    ("BV1Uu4y157D7", "C", "8分钟复盘流程拯救游戏意识——可执行复盘SOP"),
    ("BV1FaM86GEzd", "C", "节奏思路/大局观——43分钟深度意识课"),
    ("BV13rkyBHEeL", "C", "玩得更少但上分更快——效率/反面视角"),
]


def main():
    data = json.load(open(OUT_DIR / "搜索结果.json", encoding="utf-8"))
    vs = {v["bvid"]: v for v in data["videos"]}

    selected = []
    for bvid, theme, reason in PICK:
        if bvid not in vs:
            print(f"[WARN] {bvid} 不在搜索结果中")
            continue
        v = vs[bvid]
        selected.append({
            "bvid": bvid,
            "theme": theme,
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
            "hit_themes": v.get("hit_themes", []),
            "hit_keywords": v.get("hit_keywords", []),
            "入选理由": reason,
        })

    out = {
        "select_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "rule": "人工精选：覆盖三主题(A周期/B方法/C复盘)，排除手游/纯练枪/过短视频",
        "selected_count": len(selected),
        "selected": selected,
    }
    (OUT_DIR / "精选列表.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已保存精选列表.json: {len(selected)} 个视频")
    for s in selected:
        print(f"  [{s['theme']}] {s['bvid']} | play={s['play']:>7} | {s['duration']:>7} | {s['title'][:40]}")


if __name__ == "__main__":
    main()
