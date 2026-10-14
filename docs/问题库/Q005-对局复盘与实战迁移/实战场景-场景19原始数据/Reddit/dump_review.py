# -*- coding: utf-8 -*-
"""导出 round1 + round2 帖子的标题/正文要点/评论, 供撰写摘录"""
import json

for fname in ["known_posts_comments.json", "round2_posts_comments.json"]:
    p = rf"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-场景19原始数据\Reddit\{fname}"
    try:
        d = json.load(open(p, encoding="utf-8"))
    except FileNotFoundError:
        print(f"### {fname} not ready")
        continue
    print(f"\n########## {fname} ({len(d)} posts) ##########")
    for post in d:
        print(f"\n=== [{post['id']}] r/{post['subreddit']} {post['title']}")
        print(f"URL: {post['url']}")
        print(f"BODY: {post['body'][:600]}")
        for i, c in enumerate(post["comments"][:6], 1):
            print(f"  C{i} ({c['author']}): {c['body'][:350]}")
