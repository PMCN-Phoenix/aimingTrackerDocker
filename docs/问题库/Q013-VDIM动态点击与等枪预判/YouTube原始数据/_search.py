# -*- coding: utf-8 -*-
"""Search YouTube via yt-dlp for Q013 topics. Saves results to search_results.json"""
import json, time, sys
import yt_dlp

PROXY = "http://127.0.0.1:7892"

QUERIES = [
    "VDIM dynamic clicking aim",
    "LG56 Vdim explained",
    "anticipation aiming moving targets FPS",
    "predictive aiming vs reactive aiming aim trainer",
    "how to lead targets aim trainer kovaaks",
    "target velocity matching clicking timing kovaaks",
    "Kovaaks dynamic clicking tips anticipation",
    "why is my tracking slow aim trainer",
    "tracking vs flicking aim technique explained",
    "aim trainer target reading prediction",
    "rA TV aim tracking",
    "Sparky Kovaaks dynamic clicking guide",
    "DoMoe aim training method",
    "WestProter target reading aim",
    "SilkyCrisp aim mechanics tracking",
    "Aimer7 tracking guide",
    "voltiac dynamic clicking scenario guide",
    "leading moving target valorant aim",
]

opts = {
    "proxy": PROXY,
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "extract_flat": "in_playlist",
    "noplaylist": True,
    "default_search": "ytsearch10",
}

out = {}
with yt_dlp.YoutubeDL(opts) as ydl:
    for q in QUERIES:
        key = f"ytsearch10:{q}"
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
            print(f"[OK] {q} -> {len(entries)} videos", flush=True)
        except Exception as ex:
            out[q] = {"error": str(ex)}
            print(f"[FAIL] {q} -> {ex}", flush=True)
        time.sleep(2)

with open(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\YouTube原始数据\search_results.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("DONE")
