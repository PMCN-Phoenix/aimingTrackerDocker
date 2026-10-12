# -*- coding: utf-8 -*-
"""把所有字幕拼成可读文本，按 bvid 分块，方便读"""
import json
from pathlib import Path

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q002-转火微调\转火微调-B站原始数据")
SubDir = OUT_DIR / "字幕"
meta = json.loads((OUT_DIR / "视频元数据.json").read_text(encoding="utf-8"))

def fmt_ts(sec):
    m = int(sec // 60); s = int(sec % 60)
    return f"{m:02d}:{s:02d}"

out_lines = []
for f in sorted(SubDir.glob("*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    bvid = d["bvid"]
    info = meta.get(bvid, {})
    title = info.get("title", "")
    owner = info.get("owner", "")
    dur = info.get("duration", 0)
    segs = d.get("segments", [])
    out_lines.append(f"\n\n{'='*80}\n### {bvid} | {title}\nUP: {owner} | 时长: {dur}s | 字幕段数: {len(segs)}\n{'='*80}")
    for seg in segs:
        ts = fmt_ts(seg.get("from", 0))
        text = seg.get("content", "").strip()
        if text:
            out_lines.append(f"[{ts}] {text}")

text = "\n".join(out_lines)
(OUT_DIR / "_全部字幕汇总.txt").write_text(text, encoding="utf-8")
print(f"[DONE] total chars: {len(text)}, saved _全部字幕汇总.txt")
