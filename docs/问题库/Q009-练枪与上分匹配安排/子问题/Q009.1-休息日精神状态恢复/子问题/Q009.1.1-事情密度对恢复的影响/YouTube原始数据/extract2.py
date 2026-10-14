# -*- coding: utf-8 -*-
"""Q009.1.1: VTT -> timestamped txt + keyword windows."""
import re, os, glob

base = os.path.dirname(os.path.abspath(__file__))

def ts_to_sec(ts):
    hms, ms = ts.split('.')
    parts = [float(p) for p in hms.split(':')]
    if len(parts) == 3:
        h, m, s = parts
    else:
        h = 0; m, s = parts
    return h*3600 + m*60 + s

def sec_to_mmss(t):
    return f"{int(t//60):02d}:{int(t%60):02d}"

def parse_vtt(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    rows = []
    for b in content.split('\n\n'):
        lines = b.strip().split('\n')
        if len(lines) < 2: continue
        tl = None
        for i, l in enumerate(lines):
            mt = re.match(r'^(\d{2}:\d{2}:\d{2}[.,]\d{3})\s+-->', l)
            if mt:
                tl = mt.group(1); texts = lines[i+1:]; break
        if not tl: continue
        txt = re.sub(r'<[^>]+>', '', ' '.join(texts)).strip()
        if txt: rows.append((ts_to_sec(tl), txt))
    out = []
    for t, x in rows:
        if out and out[-1][1] == x: continue
        out.append((t, x))
    return out

all_vtts = sorted(glob.glob(os.path.join(base, "*.vtt")))
chosen = {}
for v in all_vtts:
    if v.endswith('.en-en.vtt'): continue
    bn = os.path.basename(v)
    bn = re.sub(r'#\.en(-[A-Za-z0-9]+)?\.vtt$', '', bn)
    is_orig = v.endswith('.en-orig.vtt')
    if bn not in chosen or not is_orig:
        chosen[bn] = v

for bn, v in chosen.items():
    rows = parse_vtt(v)
    txtpath = os.path.join(base, bn + '.txt')
    with open(txtpath, 'w', encoding='utf-8') as f:
        for t, x in rows:
            f.write(f"[{sec_to_mmss(t)}] {x}\n")
    print(f"{bn}: {len(rows)} cues <- {os.path.basename(v)}")

KW = [r'\brest', r'\bdetach', r'\bdetachment', r'\bflow', r'\bbored', r'\bboredom',
      r'\bbusy', r'\bswitch', r'\bresidue', r'\bmultitask', r'\bcognitive load',
      r'\bleisure', r'\brecovery', r'\bburnout', r'\bdistraction', r'\bwalk',
      r'\bgarden', r'\bcook', r'\bnature', r'\bscroll', r'\bendorphin', r'\brecharge',
      r'\bunwind', r'\bchill', r'\bpassive', r'\bactive recov']
pat = re.compile('|'.join(KW), re.I)

print("\n===== KEYWORD HITS =====")
for t in sorted(glob.glob(os.path.join(base, "*.txt"))):
    if t.endswith('.excerpts.txt'): continue
    with open(t, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    hits = [i for i, l in enumerate(lines) if pat.search(l)]
    windows = []
    for i in hits:
        if windows and i - windows[-1][1] <= 6:
            windows[-1] = (windows[-1][0], i)
        else:
            windows.append((i, i))
    outpath = t.replace('.txt', '.excerpts.txt')
    with open(outpath, 'w', encoding='utf-8') as fo:
        for (a, b) in windows:
            a = max(0, a-1); b = min(len(lines)-1, b+2)
            fo.write(f"\n### window {a}-{b}\n")
            fo.writelines(lines[a:b+1])
    print(f"{os.path.basename(t)}: {len(hits)} hits / {len(windows)} windows")
