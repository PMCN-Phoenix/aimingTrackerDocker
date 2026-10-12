# -*- coding: utf-8 -*-
"""Filter and rank search results for subtitle download."""
import json

IN = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q006-移动中瞄准定位\YouTube原始数据\search_results.json"

with open(IN, encoding="utf-8") as f:
    vids = json.load(f)

# Reputable coach / educational channels
GOOD_CHANNELS = {
    "woohoojin", "proguides", "skill capped", "gameleap", "red agent",
    "karhov", "tennispoint", "laurency", "how to valorant", "robo",
    "kephei", "dazs", "seagull", "trollz", "vandal", "sheepo",
    "axiom", "mixer", "coah", "coachu", "coaching",
    "everybody likes", "valorant coaching", "game leaf",
    "jolles", "gunshow", "kuda", "krug", "nate", "sliggy",
    "fpspsiko", "fps teacher", "aimpractice", "aim lab",
    "let's talk aim", "mouse sensitivity", "d2ves",
    "emberearth", "embetv", "emer", "emerald",
    "n0rdex", "nordex", "vini", "vinis", "vinnie",
    "dims", "dimsfi", "dimas", "dim",
    "plappy", "plappy aim", "plappyfps",
    "tarik", "tarik", "shroud", "shroud",
    "tenz", "nats", "less", "demon1",
    "aspas", "cherry", "zekken", "johnqt",
    "crashies", "funsteel", "leaf", "obo",
    "s0m", "ethan", "boostio", "crashies",
    "braveaf", "brave", "bravepoint",
    "lucky", "luckychaos", "luckychaos",
    "ward", "ward", "ward",
}

# Keywords that suggest coaching/educational content
COACH_KEYWORDS = ["guide", "tutorial", "how to", "coach", "coaching", "tip",
                  "improve", "explained", "master", "learn", "breakdown",
                  "mechanic", "technique", "advanced", "basics", "lesson"]

# Keywords to de-prioritize (montages, jokes, etc.)
BAD_KEYWORDS = ["montage", "funny", "meme", "clips", "highlight", "tiktok",
                "shorts", "ranked up", "gameplay only", "live", "stream"]

for v in vids:
    ch = (v.get("channel") or "").lower()
    title = (v.get("title") or "").lower()
    score = 0
    # channel reputation
    for gc in GOOD_CHANNELS:
        if gc in ch:
            score += 50
            break
    # coaching keywords in title
    for ck in COACH_KEYWORDS:
        if ck in title:
            score += 10
            break
    # bad keywords
    for bk in BAD_KEYWORDS:
        if bk in title:
            score -= 30
    # view count
    vc = v.get("view_count") or 0
    if vc >= 500000:
        score += 30
    elif vc >= 200000:
        score += 20
    elif vc >= 100000:
        score += 10
    elif vc >= 50000:
        score += 5
    # duration preference: 5-20 min tutorials
    dur = v.get("duration") or 0
    if 300 <= dur <= 1500:
        score += 10
    elif dur > 1800:
        score -= 5
    v["_score"] = score

# Sort by score
vids.sort(key=lambda x: -x["_score"])

# Print top 60 for review
print(f"Total: {len(vids)} videos\n")
print(f"{'Score':>5} | {'Views':>10} | {'Dur':>5} | {'Channel':<25} | Title")
print("-" * 120)
for v in vids[:60]:
    vc = v.get("view_count") or 0
    dur = v.get("duration") or 0
    ch = (v.get("channel") or "")[:24]
    title = (v.get("title") or "")[:70]
    print(f"{v['_score']:>5} | {vc:>10,} | {dur:>5} | {ch:<25} | {title}")
