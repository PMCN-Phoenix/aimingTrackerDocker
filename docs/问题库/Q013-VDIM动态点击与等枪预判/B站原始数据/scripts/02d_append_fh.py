# -*- coding: utf-8 -*-
import json
from pathlib import Path
OUT = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\B站原始数据")
data = json.load(open(OUT / "search_results.json", encoding="utf-8"))
sel = json.load(open(OUT / "selected_videos.json", encoding="utf-8"))

APPEND = [
    "BV1Ny4y157dd",  # FH Timing 400% 世界第一 954
    "BV1orgk66E78",  # FH Timing 400% Larger -4716
    "BV1XMUyBvEBL",  # VT Floating Heads Novice S5 1084
]
by = {v["bvid"]: v for v in data["videos"]}
exist = {v["bvid"] for v in sel["selected"]}
for b in APPEND:
    if b in exist: continue
    v = by.get(b)
    if not v:
        print(f"!! {b} 缺失"); continue
    sel["selected"].append(v)
    print(f"  + {b} | {v['title'][:60]}")
sel["selected_count"] = len(sel["selected"])
(OUT / "selected_videos.json").write_text(
    json.dumps(sel, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"总数: {len(sel['selected'])}")
