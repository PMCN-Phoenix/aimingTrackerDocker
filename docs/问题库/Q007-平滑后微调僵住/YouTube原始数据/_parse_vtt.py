# -*- coding: utf-8 -*-
"""Parse VTT subtitles and extract keyword-context passages with timestamps."""
import os, re, json, glob

VTT_DIR = os.path.dirname(os.path.abspath(__file__))

def parse_vtt(path):
    """Return list of (start_sec, text) merged cues."""
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    cues = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = re.match(r'^(\d{2}):(\d{2}):(\d{2})[.,](\d{3})\s*-->', line)
        if m:
            h, mn, s, ms = m.groups()
            start = int(h)*3600 + int(mn)*60 + int(s) + int(ms)/1000
            # gather text until blank line
            i += 1
            text_lines = []
            while i < len(lines) and lines[i].strip() != '':
                tl = lines[i].strip()
                # skip VTT tags
                tl = re.sub(r'<[^>]+>', '', tl)
                if tl:
                    text_lines.append(tl)
                i += 1
            cues.append((start, ' '.join(text_lines)))
        else:
            i += 1
    # merge adjacent cues into ~5s blocks
    merged = []
    cur_start = None
    cur_text = []
    cur_end = 0
    for start, text in cues:
        if cur_start is None:
            cur_start = start
            cur_text = [text]
            cur_end = start
        elif start - cur_end <= 2.5:
            cur_text.append(text)
            cur_end = start
        else:
            merged.append((cur_start, ' '.join(cur_text)))
            cur_start = start
            cur_text = [text]
            cur_end = start
    if cur_start is not None:
        merged.append((cur_start, ' '.join(cur_text)))
    return merged

def ts(sec):
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m:02d}:{s:02d}"

KEYWORDS = {
    'tension':   r'tension|tight|stiff|freeze|freezing|tense|relax|relaxed|shake|shaky|jitter|jittery|shakiness',
    'micro':     r'micro|small (adjust|correction|movement|aim)|fine (adjust|control|aim|tune)|tiny|precision|pixel',
    'wrist_arm': r'wrist|forearm|elbow|shoulder|arm aim|arm-aim|pivot',
    'grip':      r'grip|palm|claw|fingertip|finger',
    'transition':r'transition|switch|between|shift|move from|go from',
    'desk_pad':  r'desk|pad|floating|rest|anchor|surface|mousepad',
    'crouch':    r'crouch|peek|swing|pre.?aim|crosshair placement|hold(ing)? (an )?angle|clear(ing)? angle|stop strafe|counter strafe',
    'flick':     r'flick|flicking|snap|snap aim|reaction|start (moving|aiming)|hesitat',
}

videos_meta = {
    "9JoDMDXVTcg":  ("Solving the most common aiming issue - Tension Management Guide", "Viscose"),
    "qZu8ttjyo2Y":  ("Permanently Fix Your BAD Micro Adjusting", "4BangerKovaaks"),
    "s0BuZ4sQpsU":  ("Aim Guide for PERFECT Micro Corrections (Ep. 1)", "Zapper"),
    "EqeDWH4kcME":  ("Aim Mechanics No One Else Talks About", "West Proter"),
    "RvhniU-CJXU":  ("Is your mouse grip holding you back?", "Viscose"),
    "b3oKiXFBWjk":  ("Wrist To Arm Aiming / How To Arm Aim - In depth Guide", "Michael StarBoi"),
    "SG9XPxs-pZU":  ("The Ultimate Wrist Position For Aiming", "Struth Gaming"),
    "A3cZS3iNBGU":  ("Aiming's Best Kept Secret - Fingertip Skating", "Struth Gaming"),
    "ZEH4CfytNyo":  ("The LAST AIM ROUTINE you will EVER NEED! - VDIM", "Lowgravity56"),
    "mOsBjfOGMuU":  ("Fluidity, the Key to Static Clicking - Secrets of Aim Ep.6", "MattyOW"),
    "Eu_0SlnEeZs":  ("'But you have your whole arm to aim!'", "TCaptainX"),
    "b1X3YuT_ruk":  ("Why You Suck at Peeking (and how to fix it)", "Konpeki"),
    "LtyoXh2y-wk":  ("What's the Deal with Crouching?", "Konpeki"),
    "zGA4Rxn_Mjg":  ("5 Aim Mistakes You Don't Realize You're Making", "Konpeki"),
}

out = {}
for f in sorted(glob.glob(os.path.join(VTT_DIR, '*.en.vtt'))):
    vid = os.path.basename(f).replace('.en.vtt', '')
    if vid not in videos_meta:
        continue
    cues = parse_vtt(f)
    title, channel = videos_meta[vid]
    hits = {}
    for cat, pat in KEYWORDS.items():
        rx = re.compile(pat, re.I)
        cat_hits = []
        for start, text in cues:
            if rx.search(text):
                # clean text
                text_clean = re.sub(r'\s+', ' ', text).strip()
                if len(text_clean) > 30:
                    cat_hits.append((ts(start), text_clean[:400]))
        hits[cat] = cat_hits[:12]  # cap per category
    out[vid] = {"title": title, "channel": channel, "hits": hits, "total_cues": len(cues)}

outpath = os.path.join(VTT_DIR, '_extracted.json')
with open(outpath, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

# print summary
for vid, d in out.items():
    print(f"\n=== {vid} | {d['channel']} | {d['title']} | cues={d['total_cues']}")
    for cat, hs in d['hits'].items():
        print(f"  [{cat}] {len(hs)} hits")
print(f"\nWrote {outpath}")
