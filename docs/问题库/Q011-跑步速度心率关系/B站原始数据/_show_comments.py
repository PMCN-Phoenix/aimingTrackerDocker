# -*- coding: utf-8 -*-
import json
d = json.load(open(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q011-跑步速度心率关系\B站原始数据\comments_all.json", encoding="utf-8"))
for k, v in d.items():
    print(f"\n=== {k} ({v['label']}) ===")
    for c in v["comments"][:10]:
        print(f"  [{c.get('like',0)}赞] {c.get('message','')[:120]}")
