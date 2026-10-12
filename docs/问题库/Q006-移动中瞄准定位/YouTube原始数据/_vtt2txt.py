# -*- coding: utf-8 -*-
"""Convert all .vtt subtitle files to clean .txt (strip tags, merge lines)."""
import os, re, glob

SUB_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q006-移动中瞄准定位\YouTube原始数据\字幕"

def vtt_to_text(vtt_path):
    with open(vtt_path, encoding="utf-8") as f:
        lines = f.readlines()
    out = []
    prev_text = None
    for line in lines:
        line = line.rstrip("\n")
        # skip blank, header, timing lines
        if not line.strip():
            continue
        if line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if "-->" in line:
            continue
        # strip HTML-like tags
        text = re.sub(r"<[^>]+>", "", line)
        # skip duplicate consecutive (auto-subs often repeat)
        if text == prev_text:
            continue
        # skip NOTE lines
        if text.startswith("NOTE"):
            continue
        out.append(text)
        prev_text = text
    # Merge into paragraphs (auto-subs come line by line; just join with space)
    return " ".join(out)

# Process each .vtt, but skip .en-orig.vtt duplicates (they're same as .en.vtt)
vtt_files = glob.glob(os.path.join(SUB_DIR, "*.vtt"))
seen_ids = set()
for vp in sorted(vtt_files):
    base = os.path.basename(vp)
    # extract video ID
    m = re.match(r"([\w-]{11})_", base)
    if not m:
        continue
    vid = m.group(1)
    # Skip en-orig (duplicate)
    if ".en-orig." in base:
        continue
    if vid in seen_ids:
        continue
    seen_ids.add(vid)
    txt = vtt_to_text(vp)
    # output txt name: same base but .txt and replace vtt ext
    txt_name = base.replace(".vtt", ".txt")
    txt_path = os.path.join(SUB_DIR, txt_name)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt)
    print(f"{vid}: {len(txt)} chars -> {txt_name}")

print(f"\nProcessed {len(seen_ids)} unique videos")
