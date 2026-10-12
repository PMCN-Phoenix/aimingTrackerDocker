# -*- coding: utf-8 -*-
"""
Q002 - 抓 aid/cid via 网页 HTML window.__INITIAL_STATE__
"""
import sys, json, time, re, requests
from pathlib import Path

sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q002-转火微调\转火微调-B站原始数据")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

selected = json.loads((OUT_DIR / "精选列表.json").read_text(encoding="utf-8"))
bvids = [x["bvid"] for x in selected]

pool = BiliCookiePool()

def fetch_meta(bvid):
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Referer": "https://www.bilibili.com/"})
    s.headers["Cookie"] = pool.get_cookie()
    for attempt in range(3):
        try:
            r = s.get(f"https://www.bilibili.com/video/{bvid}/", timeout=25)
            t = r.text
            m = (re.search(r"window\.__INITIAL_STATE__=(.*?);\(function", t, re.S)
                 or re.search(r"window\.__INITIAL_STATE__=(.*?);\s*</script>", t, re.S))
            if not m:
                return {"bvid": bvid, "error": "no __INITIAL_STATE__"}
            state = json.loads(m.group(1))
            v = state.get("videoData") or {}
            info = {
                "bvid": bvid,
                "aid": v.get("aid"),
                "cid": v.get("cid"),
                "title": v.get("title"),
                "owner": (v.get("owner") or {}).get("name"),
                "duration": v.get("duration"),
                "desc": (v.get("desc") or "")[:800],
                "view": (v.get("stat") or {}).get("view"),
                "like": (v.get("stat") or {}).get("like"),
                "reply": (v.get("stat") or {}).get("reply"),
                "subtitle_list": [p.get("cid") for p in (v.get("pages") or [])],
            }
            return info
        except Exception as e:
            if attempt == 2:
                return {"bvid": bvid, "error": str(e)}
            time.sleep(2)

results = {}
for i, bv in enumerate(bvids):
    info = fetch_meta(bv)
    results[bv] = info
    if "error" in info:
        print(f"[{i+1}/30] {bv} FAIL: {info['error']}")
    else:
        print(f"[{i+1}/30] {bv} OK aid={info['aid']} cid={info['cid']} dur={info['duration']}s | {info['title'][:40]}")
    time.sleep(1.2)

(OUT_DIR / "视频元数据.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n[DONE] saved {(OUT_DIR / '视频元数据.json')}")
