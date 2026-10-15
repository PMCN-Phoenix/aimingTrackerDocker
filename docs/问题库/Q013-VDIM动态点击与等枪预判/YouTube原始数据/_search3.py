# -*- coding: utf-8 -*-
"""Third batch: Floating Heads Timing Kovaak technique."""
import json, time
import yt_dlp

PROXY = "http://127.0.0.1:7892"

QUERIES = [
    "Floating Heads Timing Kovaak technique",
    "Floating Heads 400 percent kovaaks",
    "Kovaak Floating Heads Timing tips improve score",
    "VDIM Floating Heads Timing dynamic clicking",
    "Floating Heads Timing Voltaic benchmark",
    "Kovaaks timing clicking guide how to",
    "Sparky aim training Floating Heads",
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
            print("[OK]", q, "->", len(entries), flush=True)
        except Exception as ex:
            out[q] = {"error": str(ex)}
            print("[FAIL]", q, "->", ex, flush=True)
        time.sleep(2)

with open(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\YouTube原始数据\search_results3.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("DONE3")
