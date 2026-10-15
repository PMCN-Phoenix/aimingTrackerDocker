# -*- coding: utf-8 -*-
"""人工最终精选15个"""
import json
from pathlib import Path

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\B站原始数据")
data = json.load(open(OUT_DIR / "search_results.json", encoding="utf-8"))

PICKS = [
    "BV1yw4m1a77W",  # 复用 反移动
    "BV1C2Hi6AEAa",  # 复用 微调快慢
    "BV17k4y1S7HW",  # 复用 Scucchi
    "BV13S411A7GX",  # 复用 瞄准最重要部分
    "BV1F64y1r79y",  # 复用 Kovaak定位
    "BV1zp421o7Yn",  # 复用 Kovaak法宝
    "BV1pA3Sz9EzL",  # 复用 FPS技术提升
    "BV1zUjY6iEzs",  # 中文互联网最好瞄准教学
    "BV1694y1u7ar",  # 打不到移动敌人（提前量）
    "BV1A9KpzTEHL",  # 张力控制
    "BV1mE421A7pH",  # 流畅瞄准（慢占主导）
    "BV1GhXNYkEhh",  # 顿悟微调核心
    "BV1kjwde4EZR",  # 顿悟小片-预瞄
    "BV1UV4y1k76r",  # 你开枪太急
    "BV1Rr4y1u7o6",  # FPS眼部热身
]

REUSE = {
    "BV1yw4m1a77W": ("Q003", r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q003-VDIM进步方法论\VDIM调研-B站原始数据\字幕\BV1yw4m1a77W.txt"),
    "BV1C2Hi6AEAa": ("Q003/Q007", r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q007-平滑后微调僵住\B站原始数据\字幕\BV1C2Hi6AEAa.txt"),
    "BV17k4y1S7HW": ("Q003", r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q003-VDIM进步方法论\VDIM调研-B站原始数据\字幕\BV17k4y1S7HW.txt"),
    "BV13S411A7GX": ("Q003", r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q003-VDIM进步方法论\VDIM调研-B站原始数据\字幕\BV13S411A7GX.txt"),
    "BV1F64y1r79y": ("Q003", r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q003-VDIM进步方法论\VDIM调研-B站原始数据\字幕\BV1F64y1r79y.txt"),
    "BV1zp421o7Yn": ("Q003", r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q003-VDIM进步方法论\VDIM调研-B站原始数据\字幕\BV1zp421o7Yn.txt"),
    "BV1pA3Sz9EzL": ("Q003", r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q003-VDIM进步方法论\VDIM调研-B站原始数据\字幕\BV1pA3Sz9EzL.txt"),
}

by_bvid = {v["bvid"]: v for v in data["videos"]}
picked = []
for b in PICKS:
    v = by_bvid.get(b)
    if not v:
        print(f"!! {b} 不在搜索结果中")
        continue
    v2 = dict(v)
    if b in REUSE:
        tag, path = REUSE[b]
        v2["reuse_subtitle"] = f"{tag}: {path}"
    picked.append(v2)

print(f"最终精选 {len(picked)} 个:")
for i, v in enumerate(picked):
    reuse = " [复用]" if v.get("reuse_subtitle") else " [新抓]"
    print(f"  {i+1:2d}. {v['bvid']} | play={v.get('play',0):>8} | {v['title'][:50]}{reuse}")

out = {
    "selected_time": data.get("search_time"),
    "total_searched": len(data["videos"]),
    "selected_count": len(picked),
    "selected": picked,
}
(OUT_DIR / "selected_videos.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
