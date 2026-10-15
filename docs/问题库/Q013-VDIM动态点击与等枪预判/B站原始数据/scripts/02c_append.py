# -*- coding: utf-8 -*-
"""追加5个微定位主题视频"""
import json
from pathlib import Path

OUT = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\B站原始数据")
data = json.load(open(OUT / "search_results.json", encoding="utf-8"))
sel = json.load(open(OUT / "selected_videos.json", encoding="utf-8"))

APPEND = [
    "BV1eehiz9EEc",   # 目标一动就马枪？动态定位
    "BV13QFxzCEXb",   # 微调：从原理到实操完整版
    "BV1nx421Q7fh",   # 动态点击完全攻略指南
    "BV1JqdcBGEJy",   # 微调之王Cartoon MattyOW
    "BV1ecbAznETh",   # Kovaak 手抖/抖动
]

by_bvid = {v["bvid"]: v for v in data["videos"]}
existing = {v["bvid"] for v in sel["selected"]}
added = 0
for b in APPEND:
    if b in existing:
        continue
    v = by_bvid.get(b)
    if not v:
        print(f"!! {b} 不在结果中")
        continue
    sel["selected"].append(v)
    added += 1
    print(f"  + {b} | {v['title'][:50]}")

sel["selected_count"] = len(sel["selected"])
(OUT / "selected_videos.json").write_text(
    json.dumps(sel, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n追加 {added} 个，精选总数: {len(sel['selected'])}")
