# -*- coding: utf-8 -*-
import json
from pathlib import Path
OUT = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\B站原始数据")
d = json.load(open(OUT / "search_results.json", encoding="utf-8"))
KW = ["floating", "漂浮人头", "人头", "timing", "浮頭", "漂浮"]
hits = []
for v in d["videos"]:
    t = (v.get("title") or "").lower()
    if any(k in t for k in KW):
        hits.append(v)
hits.sort(key=lambda x: -(x.get("play") or 0))
print(f"Floating Heads相关 {len(hits)} 个:")
for v in hits[:25]:
    print(f"{v['bvid']} | play={v.get('play',0):>7} fav={v.get('favorites',0):>6} | {v['title'][:60]}")
