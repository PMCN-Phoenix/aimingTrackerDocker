import os, re, glob, sys

d = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q009-练枪与上分匹配安排\YouTube原始数据"

def parse_vtt(path):
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()
    out = []
    seen = set()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
            continue
        # timestamp line
        if re.match(r'^\d{2}:\d{2}:\d{2}\.\d{3}\s*-->', line):
            continue
        # strip tags
        text = re.sub(r'<[^>]+>', '', line).strip()
        if not text:
            continue
        if text in seen:
            continue
        seen.add(text)
        out.append(text)
    return ' '.join(out)

for vtt in glob.glob(os.path.join(d, '*.vtt')):
    txt = parse_vtt(vtt)
    out = vtt.replace('.vtt', '.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(txt)
    print(os.path.basename(out), len(txt))
