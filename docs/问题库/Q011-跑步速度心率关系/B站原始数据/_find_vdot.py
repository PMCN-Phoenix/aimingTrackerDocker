# -*- coding: utf-8 -*-
import json
p = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q011-跑步速度心率关系\B站原始数据\scored_top.json"
d = json.load(open(p, encoding="utf-8"))
keywords = ["vdot", "丹尼尔斯", "心率漂移", "drift", "杰克", "jack daniels", "丹尼"]
for i, v in enumerate(d):
    t = ((v.get("title") or "") + " " + (v.get("description") or "")).lower()
    if any(k in t for k in keywords):
        print(f"{i:3d} score={v['score']:5.1f} play={v.get('play',0):7d} dur={v.get('duration')} bv={v['bvid']}")
        print(f"     title: {v['title'][:70]}")
        print(f"     UP: {v.get('author','')}")
        print()
