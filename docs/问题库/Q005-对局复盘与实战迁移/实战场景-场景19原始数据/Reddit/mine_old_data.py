# -*- coding: utf-8 -*-
"""从已有场景的 Reddit JSON 数据里挖掘心态相关帖子（带 score）"""
import json, glob, re

files = glob.glob(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景\*-Reddit原始数据\posts_with_comments_*.json")
kw = re.compile(r"anxi|nervous|tilt|scared|afraid|fear|calm|mental|pressure|panic|mindset|confidence|overthink", re.I)
seen = {}
for f in files:
    d = json.load(open(f, encoding="utf-8"))
    for p in d:
        text = (p.get("title", "") + " " + p.get("body", "") + " " + p.get("selftext", ""))[:3000]
        if kw.search(text):
            pid = p.get("id")
            if pid in seen:
                continue
            permalink = p.get("permalink", "")
            sub = p.get("subreddit") or (permalink.split("/")[2] if len(permalink.split("/")) > 2 else "?")
            seen[pid] = {
                "score": p.get("score"),
                "title": p.get("title", "")[:100],
                "sub": sub,
                "url": p.get("url") or ("https://www.reddit.com" + permalink),
                "n_comments": len(p.get("comments", []) or []),
            }
rows = sorted(seen.values(), key=lambda x: -(x["score"] or 0))
print("files scanned:", len(files))
print("relevant posts:", len(rows))
for r in rows[:40]:
    print(f"[{r['score']}] r/{r['sub']} (cmts={r['n_comments']}) {r['title']}")
    print("    ", r["url"])
