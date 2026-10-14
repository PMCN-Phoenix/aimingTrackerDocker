# -*- coding: utf-8 -*-
"""检查新发现帖子是否已在旧数据集中（带 score）"""
import json, glob

NEW_IDS = ["w051jz", "j2zwht", "sr0kvu", "1dqg87b", "oiqtt8", "w2tfhm", "xi09mp",
           "13m2kqi", "v8ou9l", "qlldt7", "yia93e", "lw29ai", "n4rg1j", "j0f4v8",
           "vrg8er", "vkg9ip", "1brbcl8", "wrn2oi", "1d3ymev", "xr7kgp", "f8ehv1",
           "1cwy4b1", "57qrwp", "2jvg7m", "9baeyd", "197doy3"]
files = glob.glob(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景\*-Reddit原始数据\posts_with_comments_*.json")
hits = {}
for f in files:
    d = json.load(open(f, encoding="utf-8"))
    for p in d:
        pid = p.get("id", "")
        for nid in NEW_IDS:
            if pid.endswith(nid) and nid not in hits:
                hits[nid] = {"score": p.get("score"), "title": p.get("title", "")[:80],
                             "n_comments": len(p.get("comments", []) or [])}
for nid in NEW_IDS:
    if nid in hits:
        print(f"[FOUND {hits[nid]['score']}] {nid}: {hits[nid]['title']} (cmts={hits[nid]['n_comments']})")
print("---")
print("found:", len(hits), "/", len(NEW_IDS))
