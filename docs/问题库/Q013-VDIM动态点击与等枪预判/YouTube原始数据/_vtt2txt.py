# -*- coding: utf-8 -*-
"""Convert a VTT subtitle file into timestamped plain text (dedupe repeated lines).
Usage: python _vtt2txt.py <in.vtt> <out.txt>
"""
import re, sys

def parse_ts(ts):
    # 00:00:01.000 or 00:01.000
    parts = ts.replace('.', ':').split(':')
    parts = [int(x) for x in parts]
    if len(parts) == 4:
        h, m, s, ms = parts
    else:
        h, m, s = 0, parts[0], parts[1]
        ms = parts[2] if len(parts) > 2 else 0
    total = h * 3600 + m * 60 + s
    return total

def main(inp, outp):
    lines = open(inp, encoding='utf-8').read().splitlines()
    entries = []
    i = 0
    pat = re.compile(r'^(\d+:\d+:[\d.]+|\d+:\d+[\d.]+)\s*-->\s*(\d+:\d+:[\d.]+|\d+:\d+[\d.]+)')
    while i < len(lines):
        m = pat.match(lines[i].strip())
        if m:
            start = parse_ts(m.group(1))
            i += 1
            text_lines = []
            while i < len(lines) and lines[i].strip() != '':
                text_lines.append(lines[i])
                i += 1
            txt = ' '.join(text_lines)
            txt = re.sub(r'<[^>]+>', '', txt)  # remove inline tags
            txt = re.sub(r'\s+', ' ', txt).strip()
            if txt:
                entries.append((start, txt))
        i += 1
    # dedupe consecutive duplicates (auto-caption repeats)
    merged = []
    for t, txt in entries:
        if merged and txt == merged[-1][1]:
            continue
        if merged and txt.endswith(merged[-1][1][-40:]) and len(txt) > len(merged[-1][1]):
            merged[-1] = (merged[-1][0], txt)
            continue
        merged.append((t, txt))
    with open(outp, 'w', encoding='utf-8') as f:
        for t, txt in merged:
            mm, ss = divmod(t, 60)
            hh, mm = divmod(mm, 60)
            stamp = f'{mm:02d}:{ss:02d}' if hh == 0 else f'{hh:02d}:{mm:02d}:{ss:02d}'
            f.write(f'[{stamp}] {txt}\n')
    print('wrote', outp, len(merged), 'lines')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
