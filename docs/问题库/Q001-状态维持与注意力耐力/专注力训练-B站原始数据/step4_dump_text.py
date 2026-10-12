# -*- coding: utf-8 -*-
"""把字幕 JSON 转成带时间戳的纯文本，便于精读"""
import json, os, glob, re

BASE = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q001-状态维持与注意力耐力\专注力训练-B站原始数据"
SUB = os.path.join(BASE, "字幕")
OUT = os.path.join(BASE, "字幕全文")
os.makedirs(OUT, exist_ok=True)

def ts(sec):
    m = int(sec // 60); s = int(sec % 60)
    return f"{m:02d}:{s:02d}"

for f in glob.glob(os.path.join(SUB, "*.json")):
    bvid = os.path.basename(f).replace(".json", "")
    segs = json.load(open(f, encoding="utf-8"))
    lines = []
    for seg in segs:
        lines.append(f"[{ts(seg.get('from',0))}] {seg.get('content','')}")
    txt = "\n".join(lines)
    open(os.path.join(OUT, f"{bvid}.txt"), "w", encoding="utf-8").write(txt)
    print(f"{bvid}: {len(segs)} 段, {len(txt)} 字")
print("done")
