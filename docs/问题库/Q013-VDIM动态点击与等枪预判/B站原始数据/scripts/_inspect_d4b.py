# -*- coding: utf-8 -*-
import json
from pathlib import Path
OUT = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\B站原始数据")
d = json.load(open(OUT / "search_results.json", encoding="utf-8"))
KW = ["微调", "抖动", "小球", "微定位", "动态定位", "动态点击", "micro", "细跟", "追踪", "small", "thin"]
hits = []
for v in d["videos"]:
    t = (v.get("title") or "")
    if any(k.lower() in t.lower() for k in KW):
        hits.append(v)
hits.sort(key=lambda x: -(x.get("play") or 0))
print(f"命中关键词的视频共 {len(hits)} 个:")
for v in hits[:30]:
    print(f"{v['bvid']} | play={v.get('play',0):>8} fav={v.get('favorites',0):>6} | {v['title'][:60]}")
