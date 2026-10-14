# -*- coding: utf-8 -*-
"""读旧数据中 wj31na (nightmares) 和 y8whtw (low elo journey) 全文"""
import json, glob

WANT = ["wj31na", "y8whtw"]
files = glob.glob(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景\*-Reddit原始数据\posts_with_comments_*.json")
found = {}
for f in files:
    d = json.load(open(f, encoding="utf-8"))
    for p in d:
        pid = p.get("id", "")
        for w in WANT:
            if pid.endswith(w) and w not in found:
                found[w] = p
for w in WANT:
    p = found.get(w)
    if not p:
        print(f"===== {w} NOT FOUND =====")
        continue
    print(f"\n===== [{p.get('score')}] {p.get('title')} =====")
    print("URL:", p.get("url") or p.get("permalink"))
    print("BODY:", (p.get("body") or p.get("selftext") or "")[:2000])
    for c in (p.get("comments") or [])[:8]:
        print(f"  -- {c.get('author')}: {(c.get('body') or '')[:500]}")
