# -*- coding: utf-8 -*-
"""Additional YouTube searches: micro-adjustment on small jittery targets."""
import json, time
import yt_dlp

PROXY = "http://127.0.0.1:7892"

QUERIES = [
    "micro adjustment aiming small targets kovaaks",
    "jittery target tracking vertical oscillation aim",
    "Thin Gauntlet aiming technique kovaaks",
    "wrist finger micro aim correction fatigue",
    "small moving target vertical jitter aim trainer",
    "Sparky aim training micro corrections",
    "over-correction aiming shaky micro adjustment fix",
    "why micro adjustments feel awkward aim trainer",
]

opts = {
    "proxy": PROXY,
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "extract_flat": "in_playlist",
    "noplaylist": True,
    "default_search": "ytsearch8",
}

out = {}
with yt_dlp.YoutubeDL(opts) as ydl:
    for q in QUERIES:
        key = f"ytsearch8:{q}"
        try:
            res = ydl.extract_info(key, download=False)
            entries = []
            for e in res.get("entries", []):
                if not e:
                    continue
                entries.append({
                    "id": e.get("id"),
                    "title": e.get("title"),
                    "channel": e.get("channel") or e.get("uploader"),
                    "duration": e.get("duration"),
                    "views": e.get("view_count"),
                    "url": f"https://www.youtube.com/watch?v={e.get('id')}",
                })
            out[q] = entries
            print(f"[OK] {q} -> {len(entries)}", flush=True)
        except Exception as ex:
            out[q] = {"error": str(ex)}
            print(f"[FAIL] {q} -> {ex}", flush=True)
        time.sleep(2)

with open(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\YouTube原始数据\search_results2.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("DONE2")
