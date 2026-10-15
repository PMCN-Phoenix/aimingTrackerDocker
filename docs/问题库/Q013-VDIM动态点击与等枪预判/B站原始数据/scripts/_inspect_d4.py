# -*- coding: utf-8 -*-
import json
from pathlib import Path
OUT = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\B站原始数据")
d = json.load(open(OUT / "search_results.json", encoding="utf-8"))
# 只看D4方向的
d4 = [v for v in d["videos"] if "D4" in (v.get("hit_themes") or [v.get("keyword_hit") or ""])]
d4.sort(key=lambda x: -(x.get("play") or 0))
print(f"D4方向共 {len(d4)} 条，按播放排序前25:")
for v in d4[:25]:
    print(f"{v['bvid']} | play={v.get('play',0):>8} fav={v.get('favorites',0):>6} | {v['title'][:60]}")
