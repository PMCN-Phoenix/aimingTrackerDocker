# -*- coding: utf-8 -*-
"""把所有评论 dump 成可读文本，按 bvid 分块，只保留高赞和有信息量的"""
import json
from pathlib import Path

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q002-转火微调\转火微调-B站原始数据")
CmtDir = OUT_DIR / "评论"

lines = []
for f in sorted(CmtDir.glob("*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    bvid = d["bvid"]
    title = d.get("title", "")[:40]
    lines.append(f"\n\n{'='*70}\n### {bvid} | {title}\n总评论数(接口)={d.get('total_count')} 主评论抓={d.get('main_fetched')} 楼中楼抓={d.get('sub_fetched')}\n{'='*70}")
    # 按赞排序主评论
    comments = d.get("comments", [])
    comments_sorted = sorted(comments, key=lambda x: -x.get("like", 0))
    for c in comments_sorted[:12]:  # top 12 主评论
        like = c.get("like", 0)
        uname = c.get("uname", "")
        msg = (c.get("message") or "").replace("\n", " ")[:300]
        lines.append(f"\n[赞{like}] {uname}: {msg}")
        # 楼中楼里挑有信息量的
        subs = c.get("subs", [])
        subs_sorted = sorted(subs, key=lambda x: -x.get("like", 0))
        for s in subs_sorted[:3]:
            smsg = (s.get("message") or "").replace("\n", " ")[:200]
            slike = s.get("like", 0)
            suname = s.get("uname", "")
            if smsg:
                lines.append(f"    └[赞{slike}] {suname}: {smsg}")

text = "\n".join(lines)
(OUT_DIR / "_全部评论汇总.txt").write_text(text, encoding="utf-8")
print(f"[DONE] chars={len(text)}")
