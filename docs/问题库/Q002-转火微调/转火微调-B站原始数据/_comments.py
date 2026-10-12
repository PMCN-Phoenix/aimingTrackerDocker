# -*- coding: utf-8 -*-
"""
Q002 - 抓评论（主评论 wbi + 楼中楼）
"""
import sys, json, time, hashlib, urllib.parse, requests
from pathlib import Path

sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q002-转火微调\转火微调-B站原始数据")
CmtDir = OUT_DIR / "评论"
CmtDir.mkdir(exist_ok=True)

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

def get_main_comments(s, mixin, bvid, aid, max_pages=8):
    """主评论 wbi 端点"""
    items = []
    total = 0
    for pn in range(1, max_pages + 1):
        p = sign({
            "oid": aid, "type": 1, "pn": pn, "ps": 20,
            "sort": 2, "web_location": "1315875",
        }, mixin)
        try:
            r = s.get("https://api.bilibili.com/x/v2/reply/wbi/main",
                      params=p, timeout=25)
            if r.status_code == 412 or '"code":-412' in r.text:
                return items, total, "412"
            d = r.json()
            if d.get("code") != 0:
                return items, total, f"code={d.get('code')} {d.get('message')}"
            dd = d.get("data") or {}
            replies = dd.get("replies") or []
            if not replies:
                break
            page = dd.get("page") or {}
            total = page.get("count", total)
            for rep in replies:
                items.append({
                    "rpid": rep.get("rpid"),
                    "uname": (rep.get("member") or {}).get("uname"),
                    "like": rep.get("like", 0),
                    "rcount": rep.get("rcount", 0),
                    "message": (rep.get("content") or {}).get("message", ""),
                    "ctime": rep.get("ctime"),
                    "subs": [],
                })
            if len(items) >= total:
                break
            time.sleep(1.3)
        except Exception as e:
            return items, total, str(e)
    return items, total, "ok"

def get_sub_comments(s, bvid, aid, root_rpid):
    """楼中楼"""
    subs = []
    for pn in range(1, 5):
        try:
            r = s.get("https://api.bilibili.com/x/v2/reply/reply",
                      params={"oid": aid, "type": 1, "root": root_rpid, "pn": pn, "ps": 20},
                      headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"},
                      timeout=25)
            if r.status_code == 412:
                return subs, "412"
            d = r.json()
            if d.get("code") != 0:
                return subs, f"code={d.get('code')}"
            dd = d.get("data") or {}
            replies = dd.get("replies") or []
            if not replies:
                break
            for rep in replies:
                subs.append({
                    "uname": (rep.get("member") or {}).get("uname"),
                    "like": rep.get("like", 0),
                    "message": (rep.get("content") or {}).get("message", ""),
                })
            page = dd.get("page") or {}
            if len(subs) >= page.get("count", 0):
                break
            time.sleep(1.0)
        except Exception as e:
            return subs, str(e)
    return subs, "ok"

# 主循环
summary = []
s = new_session()
mixin = get_mixin(s)

for i, (bvid, info) in enumerate(meta.items()):
    if "error" in info or not info.get("aid"):
        print(f"[{i+1}/30] {bvid} SKIP (no aid)")
        continue
    aid = info["aid"]
    title = info.get("title", "")[:30]
    print(f"[{i+1}/30] {bvid} fetching main comments...")
    items, total, status = get_main_comments(s, mixin, bvid, aid)
    if status == "412":
        pool.report_412()
        print(f"    [412] switching account, retry...")
        time.sleep(3)
        s = new_session()
        mixin = get_mixin(s)
        items, total, status = get_main_comments(s, mixin, bvid, aid)
    print(f"    main: {len(items)}/{total} status={status}")
    # 抓楼中楼（只对 rcount>0 且前 15 条主评论）
    sub_count = 0
    for rep in items[:15]:
        if rep["rcount"] and rep["rcount"] > 0:
            subs, sstat = get_sub_comments(s, bvid, aid, rep["rpid"])
            rep["subs"] = subs
            sub_count += len(subs)
            if sstat == "412":
                pool.report_412()
                s = new_session()
                mixin = get_mixin(s)
            time.sleep(0.8)
    pool.report_success()
    out = {
        "bvid": bvid,
        "aid": aid,
        "title": info.get("title"),
        "owner": info.get("owner"),
        "total_count": total,
        "main_fetched": len(items),
        "sub_fetched": sub_count,
        "status": status,
        "comments": items,
    }
    (CmtDir / f"{bvid}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    summary.append({"bvid": bvid, "main": len(items), "subs": sub_count, "total": total, "status": status})
    time.sleep(1.5)

(OUT_DIR / "评论抓取汇总.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n[DONE] {len(summary)} videos, see 评论/ folder")
