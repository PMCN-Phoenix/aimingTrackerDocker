# -*- coding: utf-8 -*-
"""Rank search results by authority + title relevance + views."""
import json

IN = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景\18-拉出去打不到人-YouTube原始数据\search_results.json"

AUTHOR_CHANNELS = [
    "woohoojin", "boostroom", "riddbtw", "konpeki", "zapper", "nAts",
    "rem", "gameleap", "coach mills", "kariev", "nuketown", "let's talk",
    "dazs", "michalek", "skill-capped", "thespike.gg", "jollztv", "curved",
    "virre", "kofree", "eggwick", "dielords", "splendid shot", "roca",
    "tenz", "screaM", "aspas", "less",
]
# 标题相关词权重
TITLE_HITS = [
    ("miss", 3), ("swing", 3), ("peek", 3), ("overshoot", 3), ("overflick", 3),
    ("flick", 2), ("crosshair placement", 3), ("preaim", 2), ("pre-aim", 2),
    ("pre aim", 2), ("aim", 1), ("whiff", 3), ("head level", 2), ("eye", 2),
    ("pre fire", 2), ("prefire", 2), ("counter strafe", 1), ("pressure", 1),
    ("gunfight", 2), ("duel", 1), ("fix", 1), ("guide", 0), ("tutorial", 0),
]
# 排除：集锦/比赛/短视频
BAD_TITLE = ["highlights", "montage", "clips", "stream moments", "best of",
             "shorts", "live ", "pro pack", "crosshair code", "settings only"]

def score(r):
    t = (r.get("title") or "").lower()
    ch = (r.get("channel") or "").lower()
    if r.get("already_in_corpus"):
        return -99, ""
    s = 0
    why = []
    for a in AUTHOR_CHANNELS:
        if a in ch:
            s += 30; why.append(f"author:{a}")
            break
    for kw, w in TITLE_HITS:
        if kw in t:
            s += w; why.append(f"title:{kw}({w})")
    for b in BAD_TITLE:
        if b in t:
            s -= 40; why.append(f"bad:{b}")
    # 时长：3~20分钟教学最佳
    dur = r.get("duration") or 0
    if dur < 60:
        s -= 20; why.append("too short")
    elif dur > 1500:
        s -= 5; why.append("long")
    elif 180 <= dur <= 1200:
        s += 5; why.append("sweet duration")
    # 播放量对数
    vc = r.get("view_count") or 0
    if vc > 500000:
        s += 10
    elif vc > 100000:
        s += 7
    elif vc > 30000:
        s += 4
    elif vc > 5000:
        s += 1
    return s, ",".join(why)

def main():
    with open(IN, encoding="utf-8") as f:
        rows = json.load(f)
    scored = []
    for r in rows:
        s, why = score(r)
        if s > -99:
            scored.append((s, why, r))
    scored.sort(key=lambda x: -x[0])
    print(f"{'score':>5} | {'dur':>5} | {'views':>9} | channel | title")
    for s, why, r in scored[:40]:
        vc = r.get("view_count") or 0
        dur = r.get("duration") or 0
        print(f"{s:>5} | {dur//60:>3}:{dur%60:02d} | {vc:>9,} | {r.get('channel','')[:28]:28} | {r.get('title','')[:70]}")
        print(f"       {r['url']}   [{why}]")

if __name__ == "__main__":
    main()
