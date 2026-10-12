# -*- coding: utf-8 -*-
"""Search YouTube for Valorant movement-aim related keywords and dump metadata."""
import json, sys, time
import yt_dlp

PROXY = "http://127.0.0.1:7892"
OUT = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q006-移动中瞄准定位\YouTube原始数据\search_results.json"

QUERIES = [
    ("Movement Aim",   "valorant movement aim"),
    ("Movement Aim",   "how to aim while moving valorant"),
    ("Movement Aim",   "moving and shooting valorant"),
    ("Counter Strafe", "counter strafe aiming valorant"),
    ("Counter Strafe", "counter strafe timing valorant"),
    ("Counter Strafe", "how to counter strafe valorant"),
    ("Strafe Aiming",  "strafe aiming technique valorant"),
    ("Strafe Aiming",  "valorant strafe aim tutorial"),
    ("Strafe Aiming",  "moving target aim valorant"),
    ("Peek Aim",       "peek aim timing valorant"),
    ("Peek Aim",       "how to peek and aim valorant"),
    ("Peek Aim",       "wide peek valorant aim"),
    ("Aim Guide",      "valorant aim guide advanced"),
    ("Aim Guide",      "valorant positioning and aim"),
    ("Aim Guide",      "Woohoojin aim guide"),
]

YDL_OPTS = {
    "proxy": PROXY,
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "extract_flat": "in_playlist",  # fast: only metadata from search results
}

def main():
    all_results = {}
    seen_ids = set()
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        for group, q in QUERIES:
            search_key = f"ytsearch15:{q}"
            print(f"\n=== [{group}] searching: {q} ===", flush=True)
            try:
                info = ydl.extract_info(search_key, download=False)
            except Exception as e:
                print(f"  ERROR: {e}", flush=True)
                continue
            entries = info.get("entries", []) or []
            cnt = 0
            for e in entries:
                if not e:
                    continue
                vid = e.get("id")
                if not vid or vid in seen_ids:
                    continue
                seen_ids.add(vid)
                rec = {
                    "group": group,
                    "search_query": q,
                    "id": vid,
                    "title": e.get("title", ""),
                    "channel": e.get("channel") or e.get("uploader", ""),
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "duration": e.get("duration"),
                    "view_count": e.get("view_count"),
                    "upload_date": e.get("upload_date"),
                    "description": (e.get("description") or "")[:300],
                }
                all_results[vid] = rec
                cnt += 1
            print(f"  -> {cnt} new videos (total unique: {len(all_results)})", flush=True)
            time.sleep(1)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(list(all_results.values()), f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(all_results)} unique videos to {OUT}", flush=True)

if __name__ == "__main__":
    main()
