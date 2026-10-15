# -*- coding: utf-8 -*-
import json
from pathlib import Path
d = json.load(open(r'D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\B站原始数据\search_results.json', encoding='utf-8'))
vs = sorted(d['videos'], key=lambda x: -(x.get('play') or 0))[:40]
for v in vs:
    print(f"{v['bvid']} | play={v.get('play',0):>8} | fav={v.get('favorites',0):>6} | {v['title'][:55]} | kw={v.get('source_keyword','')[:20]}")
