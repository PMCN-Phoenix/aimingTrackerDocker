# -*- coding: utf-8 -*-
import json, re, sys, os

VTT_DIR = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(VTT_DIR, '_extracted.json'), encoding='utf-8'))

def dedup(t):
    parts = t.split()
    out = []
    for w in parts:
        if not out or out[-1] != w:
            out.append(w)
    s = ' '.join(out)
    # collapse triple repetition of a 20+ char phrase
    s = re.sub(r'(.{20,}?)\1{2,}', r'\1', s)
    return s

vids = sys.argv[1:] if len(sys.argv) > 1 else list(d.keys())
for vid in vids:
    if vid not in d:
        continue
    v = d[vid]
    print('\n========================================')
    print('### %s - %s [%s]' % (v['channel'], v['title'], vid))
    for cat, hs in v['hits'].items():
        if not hs:
            continue
        print('\n[%s]' % cat)
        for t, tx in hs:
            print('  %s: %s' % (t, dedup(tx)[:320]))
