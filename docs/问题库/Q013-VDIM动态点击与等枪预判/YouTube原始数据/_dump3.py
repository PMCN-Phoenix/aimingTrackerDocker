# -*- coding: utf-8 -*-
import json
d = json.load(open(r'D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\YouTube原始数据\search_results3.json', encoding='utf-8'))
seen = {}
for q, vids in d.items():
    print('=== QUERY:', q)
    if isinstance(vids, dict):
        print('  ERROR:', vids)
        continue
    for v in vids:
        if v['id'] in seen:
            continue
        seen[v['id']] = 1
        dur = v.get('duration') or 0
        mm = dur // 60 if dur else '?'
        views = v.get('views') or 0
        ch = (v.get('channel') or '?')[:30]
        title = (v.get('title') or '')[:85]
        print('  {} | {:>9,} | {}min | {:30} | {}'.format(v['id'], views, mm, ch, title))
