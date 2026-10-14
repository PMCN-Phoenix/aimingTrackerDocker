# -*- coding: utf-8 -*-
"""VTT -> timestamped plain text, and keyword-anchored excerpt extractor."""
import re, os, glob, sys

base = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q009-练枪与上分匹配安排\子问题\Q009.1-休息日精神状态恢复\YouTube原始数据"

def ts_to_sec(ts):
    # 00:00:01.234
    hms, ms = ts.split('.')
    parts = [float(p) for p in hms.split(':')]
    if len(parts) == 3:
        h, m, s = parts
    else:
        h = 0; m, s = parts
    return h*3600 + m*60 + s

def sec_to_mmss(t):
    m = int(t // 60); s = int(t % 60)
    return f"{m:02d}:{s:02d}"

def parse_vtt(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    rows = []
    blocks = content.split('\n\n')
    for b in blocks:
        lines = b.strip().split('\n')
        if len(lines) < 2: continue
        tl = None
        for i, l in enumerate(lines):
            mt = re.match(r'^(\d{2}:\d{2}:\d{2}[.,]\d{3})\s+-->', l)
            if mt:
                tl = mt.group(1); texts = lines[i+1:]; break
        if not tl: continue
        txt = ' '.join(texts)
        txt = re.sub(r'<[^>]+>', '', txt).strip()
        if not txt: continue
        rows.append((ts_to_sec(tl), txt))
    # dedupe repeated lines (auto-subs repeat)
    out = []
    for t, x in rows:
        if out and out[-1][1] == x: continue
        out.append((t, x))
    return out

# step 1: build .txt with timestamps for every vtt (prefer .en.vtt non-orig, fall back to -orig)
all_vtts = sorted(glob.glob(os.path.join(base, "*.vtt")))
chosen = {}
for v in all_vtts:
    if v.endswith('.en-en.vtt'): continue
    base_name = os.path.basename(v).replace('#.en-orig.vtt', '').replace('#.en.vtt', '')
    is_orig = v.endswith('.en-orig.vtt')
    if base_name not in chosen or (not is_orig):
        chosen[base_name] = v
vtts = list(chosen.values())
for v in vtts:
    rows = parse_vtt(v)
    txtpath = v.replace('.vtt', '.txt')
    with open(txtpath, 'w', encoding='utf-8') as f:
        for t, x in rows:
            f.write(f"[{sec_to_mmss(t)}] {x}\n")
    print(f"{os.path.basename(v)}: {len(rows)} cues")

# step 2: keyword excerpt extraction
KW = [r'\brest day', r'\brest days?\b', r'\bactive recovery', r'\bfatigue', r'\bburnout',
      r'\bsleep', r'\bdopamine', r'\bovertrain', r'\btake a break', r'\boff.?game',
      r'\bmental state', r'\bmental health', r'\bscreen time', r'\bsunlight|sunlight',
      r'\bexercise|work out|walking|walk\b', r'\brecharge|recovery', r'\brest week|deload']
pat = re.compile('|'.join(KW), re.I)

print("\n===== KEYWORD HITS =====")
for v in sorted(glob.glob(os.path.join(base, "*.txt"))):
    if v.endswith('.excerpts.txt'): continue
    name = os.path.basename(v)
    with open(v, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    hits = []
    for i, l in enumerate(lines):
        if pat.search(l):
            hits.append(i)
    # merge nearby hits into windows
    windows = []
    for i in hits:
        if windows and i - windows[-1][1] <= 6:
            windows[-1] = (windows[-1][0], i)
        else:
            windows.append((i, i))
    print(f"\n--- {name}: {len(hits)} hits, {len(windows)} windows ---")
    outpath = v.replace('.txt', '.excerpts.txt')
    with open(outpath, 'w', encoding='utf-8') as fo:
        for (a, b) in windows:
            a = max(0, a-1); b = min(len(lines)-1, b+2)
            fo.write(f"\n### window {a}-{b}\n")
            fo.writelines(lines[a:b+1])
    print(f"  -> {os.path.basename(outpath)}")
