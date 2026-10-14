# -*- coding: utf-8 -*-
"""Search YouTube for 'swing out and can't hit' gap topics; exclude already-fetched IDs."""
import json, time
import yt_dlp

PROXY = "http://127.0.0.1:7897"
OUT = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景\18-拉出去打不到人-YouTube原始数据\search_results.json"

# 已下载过的视频ID（Q006/Q007/Q009 字幕库），避免重复下载
EXISTING_IDS = {
    # Q006
    "m_n2lvHbsM", "kLekH9Ja3iY", "yZ-LkfEvv2k", "q6qv17jgLY4", "x8hb3RQBBF0",
    "tDC2vISCHHA", "mnQoX4JKORU", "bv6V9hoL8TY", "UDGxQ1c6t1I", "htbLDNSFQ6c",
    "b1X3YuT_ruk", "nF7CYbtBGzw", "zRQsK2VsTwY", "RhqFtgspnSo", "vmm6yo6Bsoo",
    "h65j2UglIJ0", "xbELlTvmY2k", "OesHJ312p1Y", "PssMw773_iY",
    # Q007
    "RvhniU-CJXU", "SG9XPxs-pZU", "A3cZS3iNBGU", "ZEH4CfytNyo", "9JoDMDXVTcg",
    "qZu8ttjyo2Y", "s0BuZ4sQpsU", "EqeDWH4kcME", "b3oKiXFBWjk", "mOsBjfOGMuU",
    "Eu_0SlnEeZs", "LtyoXh2y-wk", "zGA4Rxn_Mjg",
    # Q009
    "KwCzQmSx-p0", "VARQNEdQYbw", "yqyy4j32hWk", "MxbEz8ErXm0", "0t5EHc4pukM",
    "C_JPXMBzXj4", "F5Tj4akXGWM", "0nyLy4kSEww",
}

QUERIES = [
    ("SwingMiss",    "why can't i hit after swinging valorant"),
    ("SwingMiss",    "valorant swing out and miss every duel"),
    ("SwingMiss",    "why do you miss easy shots valorant"),
    ("PeekChoice",   "jiggle peek vs wide swing valorant when to use"),
    ("PeekChoice",   "how to peek angles valorant crosshair placement"),
    ("PeekChoice",   "valorant pre aim guide holding angles"),
    ("FlickOvershoot", "valorant flick overshoot fix"),
    ("FlickOvershoot", "valorant why do i overflick"),
    ("FlickOvershoot", "valorant snap shot too far past head"),
    ("VisualAim",    "valorant aim with your eyes first"),
    ("VisualAim",    "valorant visual aiming technique"),
    ("VisualAim",    "look at target not crosshair valorant"),
    ("SwingStopShoot", "valorant swing stop shoot timing"),
    ("SwingStopShoot", "valorant how to one tap after peeking"),
    ("SwingStopShoot", "Woohoojin peek guide"),
]

YDL_OPTS = {
    "proxy": PROXY,
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "extract_flat": "in_playlist",
}

def main():
    all_results = {}
    seen_ids = set()
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        for group, q in QUERIES:
            search_key = f"ytsearch12:{q}"
            print(f"\n=== [{group}] searching: {q} ===", flush=True)
            try:
                info = ydl.extract_info(search_key, download=False)
            except Exception as e:
                print(f"  ERROR: {e}", flush=True)
                time.sleep(5)
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
                    "already_in_corpus": vid in EXISTING_IDS,
                }
                all_results[vid] = rec
                cnt += 1
            print(f"  -> {cnt} new videos (total unique: {len(all_results)})", flush=True)
            time.sleep(2)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(list(all_results.values()), f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(all_results)} unique videos to {OUT}", flush=True)

if __name__ == "__main__":
    main()
