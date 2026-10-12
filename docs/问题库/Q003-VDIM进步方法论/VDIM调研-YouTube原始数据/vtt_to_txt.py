# -*- coding: utf-8 -*-
"""批量把VTT转纯文本（去重连续行，保留时间戳）。"""
import os, re, glob

D = os.path.dirname(os.path.abspath(__file__))
for vtt in glob.glob(os.path.join(D, "*.en.vtt")):
    with open(vtt, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")
    out = []
    prev = ""
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith("WEBVTT") or ln.startswith("Kind:") or ln.startswith("Language:"):
            continue
        if "-->" in ln:
            continue
        # 去 inline tags
        ln = re.sub(r"<[^>]+>", "", ln).strip()
        if not ln or ln == prev:
            continue
        prev = ln
        out.append(ln)
    txt = "\n".join(out)
    base = os.path.splitext(vtt)[0]
    with open(base + ".txt", "w", encoding="utf-8") as f:
        f.write(txt)
    print(f"{os.path.basename(base)}: {len(txt)} chars", flush=True)
print("ALL DONE")
