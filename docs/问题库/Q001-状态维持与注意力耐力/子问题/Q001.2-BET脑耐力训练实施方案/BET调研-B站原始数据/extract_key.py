# -*- coding: utf-8 -*-
"""提取所有字幕纯文本，搜索关键段落"""
import json, os, glob

SUB_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q001-状态维持与注意力耐力\子问题\Q001.2-BET脑耐力训练实施方案\BET调研-B站原始数据\字幕"

KEYWORDS = ['n-back', 'N-back', '工作记忆', '认知负荷', 'stroop', 'Stroop', '耐力', '疲劳', '双任务', 'dual task', '训练效果', '提升', '前额叶', '注意力']

for f in sorted(glob.glob(os.path.join(SUB_DIR, '*.json'))):
    bvid = os.path.basename(f).replace('.json', '')
    with open(f, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    # 拼接成带时间戳的文本
    lines = []
    for seg in data:
        content = seg.get('content', '').strip()
        if content:
            t = int(seg.get('from', 0))
            m, s = divmod(t, 60)
            lines.append(f"[{m:02d}:{s:02d}] {content}")
    full_text = ' '.join(lines)
    
    # 搜索关键词上下文
    hits = []
    for kw in KEYWORDS:
        idx = 0
        while True:
            pos = full_text.lower().find(kw.lower(), idx)
            if pos == -1:
                break
            start = max(0, pos - 80)
            end = min(len(full_text), pos + 120)
            context = full_text[start:end].replace('\n', ' ')
            hits.append(f"  [{kw}] ...{context}...")
            idx = pos + len(kw)
            if len(hits) >= 5:
                break
        if len(hits) >= 5:
            break
    
    if hits:
        print(f"\n{'='*60}")
        print(f"BV: {bvid} ({len(data)}段)")
        print(f"{'='*60}")
        for h in hits[:5]:
            print(h)
