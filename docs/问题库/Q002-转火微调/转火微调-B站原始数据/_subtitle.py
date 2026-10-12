# -*- coding: utf-8 -*-
"""
Q002 - 抓字幕（wbi /x/player/wbi/v2）
"""
import sys, json, time, hashlib, urllib.parse, requests
from pathlib import Path

sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q002-转火微调\转火微调-B站原始数据")
SubDir = OUT_DIR / "字幕"
SubDir.mkdir(exist_ok=True)

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

meta = json.loads((OUT_DIR / "视频元数据.json").read_text(encoding="utf-8"))
pool = BiliCookiePool()

def new_session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Referer": "https://www.bilibili.com/"})
    s.headers["Cookie"] = pool.get_cookie()
    return s

def get_mixin(s):
    nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=20).json()
    wbi = nav["data"]["wbi_img"]
    img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
    return "".join((img + sub)[i] for i in MIXIN)[:32]

def sign(p, mixin):
    p = dict(p)
    p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q + mixin).encode()).hexdigest()
    return p

def fetch_subtitle(s, mixin, bvid, cid):
    p = sign({"bvid": bvid, "cid": str(cid), "web_location": "333.1007"}, mixin)
    r = s.get("https://api.bilibili.com/x/player/wbi/v2", params=p,
              headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"}, timeout=20)
    if r.status_code == 412:
        return None, "412"
    d = r.json()
    subs = ((d.get("data") or {}).get("subtitle") or {}).get("subtitles") or []
    if not subs:
        return None, "no_subtitle"
    # 选语言
    pick = None
    for pref in ["zh-Hans", "zh-CN", "zh", "ai-zh", "en-US", "en"]:
        for x in subs:
            if x.get("lan") == pref:
                pick = x; break
        if pick: break
    if not pick:
        pick = subs[0]
    url = pick.get("subtitle_url", "")
    if not url:
        return None, "empty_url"
    if url.startswith("//"):
        url = "https:" + url
    body = s.get(url, headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"}, timeout=25).json()
    return body.get("body") or [], f"ok lang={pick.get('lan')}"

s = new_session()
mixin = get_mixin(s)

results = []
for i, (bvid, info) in enumerate(meta.items()):
    if "error" in info or not info.get("cid"):
        continue
    cid = info["cid"]
    print(f"[{i+1}/30] {bvid} fetching subtitle...")
    body, status = fetch_subtitle(s, mixin, bvid, cid)
    if status == "412":
        pool.report_412()
        time.sleep(3)
        s = new_session()
        mixin = get_mixin(s)
        body, status = fetch_subtitle(s, mixin, bvid, cid)
    if body:
        (SubDir / f"{bvid}.json").write_text(
            json.dumps({"bvid": bvid, "status": status, "segments": body}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        # 覆盖度检查
        last_to = max((seg.get("to", 0) for seg in body), default=0)
        dur = info.get("duration") or 0
        cov = last_to / dur if dur else 0
        print(f"    OK {len(body)} segs, cover={cov:.2f} | {info.get('title','')[:30]}")
    else:
        print(f"    FAIL {status} | {info.get('title','')[:30]}")
    results.append({"bvid": bvid, "status": status, "segs": len(body) if body else 0})
    pool.report_success()
    time.sleep(1.3)

(OUT_DIR / "字幕抓取汇总.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
ok = sum(1 for r in results if r["segs"] > 0)
print(f"\n[DONE] {ok}/{len(results)} videos have subtitles")
