import os, re, glob

d = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q009-练枪与上分匹配安排\YouTube原始数据"

def parse_vtt_ts(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    # split into cues by blank line
    cues = re.split(r'\n\n+', content)
    out = []
    for cue in cues:
        m = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->', cue)
        if not m:
            continue
        ts = m.group(1)
        # convert to mm:ss
        h, mn, s = ts.split(':')
        s = s.split('.')[0]
        ts_short = f"{int(mn):02d}:{int(s):02d}" if h == '00' else f"{int(h)}:{int(mn):02d}:{int(s):02d}"
        # last line(s) are text
        lines = cue.split('\n')
        text_lines = []
        for line in lines:
            if '-->' in line: continue
            if not line.strip(): continue
            if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'): continue
            text_lines.append(line)
        text = re.sub(r'<[^>]+>', '', ' '.join(text_lines)).strip()
        if text:
            out.append(f"[{ts_short}] {text}")
    return out

# For each vtt, write a timestamped txt
for vtt in glob.glob(os.path.join(d, '*.vtt')):
    cues = parse_vtt_ts(vtt)
    out = vtt.replace('.vtt', '.ts.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cues))
    print(os.path.basename(out), len(cues))
