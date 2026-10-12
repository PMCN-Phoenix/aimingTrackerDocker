# -*- coding: utf-8 -*-
"""把所有评论按点赞排序输出，便于精读反面意见和社区声音"""
import json, os, glob

BASE = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q001-状态维持与注意力耐力\专注力训练-B站原始数据"
CDIR = os.path.join(BASE, "评论")

out_lines = []
for f in sorted(glob.glob(os.path.join(CDIR, "*.json"))):
    bvid = os.path.basename(f).replace(".json", "")
    d = json.load(open(f, encoding="utf-8"))
    title = d.get("title", "")[:40]
    total = d.get("comment_total", 0)
    comments = d.get("comments", [])
    # 按点赞排序
    comments_sorted = sorted(comments, key=lambda x: x.get("like", 0), reverse=True)
    out_lines.append(f"\n{'='*70}\n{bvid} | {title} | 总评论{total} 抓{len(comments)}\n{'='*70}")
    for c in comments_sorted[:15]:
        msg = c.get("message", "").replace("\n", " ")[:200]
        out_lines.append(f"  [{c.get('like',0)}赞] {c.get('uname','')}: {msg}")
        for s in c.get("subs", [])[:3]:
            smsg = s.get("message", "").replace("\n", " ")[:150]
            out_lines.append(f"      ↳[{s.get('like',0)}赞] {s.get('uname','')}: {smsg}")

open(os.path.join(BASE, "评论汇总.txt"), "w", encoding="utf-8").write("\n".join(out_lines))
print(f"written, {len(out_lines)} lines")
