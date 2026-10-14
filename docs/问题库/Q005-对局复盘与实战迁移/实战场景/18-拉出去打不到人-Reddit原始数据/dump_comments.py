# -*- coding: utf-8 -*-
import json
from pathlib import Path
OUT = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景\18-拉出去打不到人-Reddit原始数据")
data = json.load(open(OUT / "posts_with_comments_18_swing_miss.json", encoding="utf-8"))
lines = []
for p in data:
    lines.append("=" * 100)
    lines.append(p["url"] + " | " + str(p.get("title")))
    lines.append("SELFTEXT: " + (p.get("selftext") or "")[:1200])
    for c in p.get("comments", [])[:12]:
        lines.append("--- @" + c["author"])
        lines.append(c["body"][:900])
(OUT / "_dump_read.txt").write_text("\n".join(lines), encoding="utf-8")
print("written", len(lines))
