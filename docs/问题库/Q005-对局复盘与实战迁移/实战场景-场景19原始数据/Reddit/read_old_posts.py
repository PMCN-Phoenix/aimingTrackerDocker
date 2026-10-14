# -*- coding: utf-8 -*-
"""从旧数据 JSON 中读指定帖子的正文+评论全文"""
import json, glob, sys

WANT = ["ye61jz", "r921lq", "fzy5es", "kcz227", "ojlxvi", "qwp2et", "w051jz"]
files = glob.glob(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景\*-Reddit原始数据\posts_with_comments_*.json")

found = {}
for f in files:
    d = json.load(open(f, encoding="utf-8"))
    for p in d:
        pid = p.get("id", "")
        if any(pid.endswith(w) or pid == w for w in WANT) and pid not in found:
            found[pid] = p

for pid in WANT:
    key = next((k for k in found if k.endswith(pid)), None)
    p = found.get(key) if key else None
    if not p:
        print(f"\n===== {pid} NOT IN OLD DATA =====")
        continue
    print(f"\n===== [{p.get('score')}] {p.get('title')} =====")
    print("URL:", p.get("url") or p.get("permalink"))
    print("BODY:", (p.get("body") or p.get("selftext") or "")[:1800])
    for c in (p.get("comments") or [])[:8]:
        print(f"  -- {c.get('author')}: {(c.get('body') or '')[:600]}")
