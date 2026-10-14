# -*- coding: utf-8 -*-
"""精确导出要引用的帖子正文+评论全文"""
import json

def load(f):
    return json.load(open(f, encoding="utf-8"))

ROUND1 = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-场景19原始数据\Reddit\known_posts_comments.json"
ROUND2 = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-场景19原始数据\Reddit\round2_posts_comments.json"

d1 = load(ROUND1)
d2 = load(ROUND2)
D = {p["id"]: p for p in d1 + d2}

# 要打印全文的帖子 id
WANT = ["w051jz", "oiqtt8", "v8ou9l", "n4rg1j", "j0f4v8", "vkg9ip", "xr7kgp", "f8ehv1", "1cwy4b1", "1dqg87b", "w2tfhm"]
for pid in WANT:
    p = D[pid]
    print(f"\n===== [{pid}] {p['title']}")
    print(f"BODY: {p['body']}")
    for i, c in enumerate(p["comments"], 1):
        print(f"  C{i} {c['author']}: {c['body']}")
