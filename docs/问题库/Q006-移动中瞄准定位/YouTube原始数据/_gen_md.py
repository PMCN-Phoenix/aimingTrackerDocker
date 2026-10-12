# -*- coding: utf-8 -*-
"""Generate markdown files from search_results.json and selected_videos.json."""
import json, os

BASE = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q006-移动中瞄准定位\YouTube原始数据"

with open(os.path.join(BASE, "search_results.json"), encoding="utf-8") as f:
    all_vids = json.load(f)
with open(os.path.join(BASE, "selected_videos.json"), encoding="utf-8") as f:
    selected = json.load(f)

# 1. Full search results
lines = ["# YouTube搜索结果-全部", "", f"共 {len(all_vids)} 个视频（按搜索组分类）", ""]
from collections import defaultdict
by_group = defaultdict(list)
for v in all_vids:
    by_group[v["group"]].append(v)

for group in ["Movement Aim", "Counter Strafe", "Strafe Aiming", "Peek Aim", "Aim Guide"]:
    vids = by_group.get(group, [])
    lines.append(f"\n## {group}（{len(vids)}个）\n")
    lines.append("| 标题 | 频道 | 观看量 | 时长 | URL |")
    lines.append("|---|---|---:|---:|---|")
    for v in sorted(vids, key=lambda x: -(x.get("view_count") or 0)):
        vc = v.get("view_count") or 0
        dur = v.get("duration") or 0
        mins = dur // 60
        secs = dur % 60
        title = v.get("title", "").replace("|", "\\|")
        ch = v.get("channel", "").replace("|", "\\|")
        lines.append(f"| {title} | {ch} | {vc:,} | {mins}:{secs:02d} | {v['url']} |")

with open(os.path.join(BASE, "YouTube搜索结果-全部.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"Wrote YouTube搜索结果-全部.md ({len(all_vids)} videos)")

# 2. Selected videos list
lines2 = ["# YouTube精选视频列表", "", f"精选 {len(selected)} 个视频", ""]
lines2.append("| # | 标题 | 频道 | 观看量 | 时长 | 字幕 | URL |")
lines2.append("|---:|---|---|---:|---:|---|---|")
subtitle_ids = set()
import glob
for fp in glob.glob(os.path.join(BASE, "字幕", "*.txt")):
    b = os.path.basename(fp)
    vid = b[:11]
    subtitle_ids.add(vid)

for i, v in enumerate(selected, 1):
    vc = v.get("view_count") or 0
    dur = v.get("duration") or 0
    mins = dur // 60
    secs = dur % 60
    title = v.get("title", "").replace("|", "\\|")
    ch = v.get("channel", "").replace("|", "\\|")
    has_sub = "✅" if v["id"] in subtitle_ids else "❌ 未抓到"
    lines2.append(f"| {i} | {title} | {ch} | {vc:,} | {mins}:{secs:02d} | {has_sub} | {v['url']} |")

with open(os.path.join(BASE, "YouTube精选视频列表.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines2))
print(f"Wrote YouTube精选视频列表.md ({len(selected)} videos, {len(subtitle_ids)} with subs)")
