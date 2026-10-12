# -*- coding: utf-8 -*-
"""从 video_data.json 提取每个视频的高赞评论（主评论+楼中楼），输出精华文本。"""
import json, os

D = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(D, "video_data.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

out = []
for bvid, v in data.items():
    title = v.get("title", "")
    out.append(f"\n{'='*60}\n{bvid} | {title}\n{'='*60}")
    comments = v.get("comments", [])
    # 按赞排序
    top = sorted(comments, key=lambda x: -(x.get("like") or 0))[:8]
    for c in top:
        likes = c.get("like", 0)
        msg = (c.get("message") or "").replace("\n", " ")[:200]
        if not msg:
            continue
        out.append(f"[{likes}赞] {msg}")
        subs = c.get("subs") or []
        for s in sorted(subs, key=lambda x: -(x.get("like") or 0))[:3]:
            sm = (s.get("message") or "").replace("\n", " ")[:150]
            if sm:
                out.append(f"  ↳ [{s.get('like',0)}赞] {sm}")

with open(os.path.join(D, "评论精华.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print(f"done, {len(out)} lines")
