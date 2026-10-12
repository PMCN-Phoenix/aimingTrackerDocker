# -*- coding: utf-8 -*-
"""B站精选视频：网页HTML取aid/cid → 评论(含楼中楼) → wbi AI字幕。"""
import sys, os, time, json, re, hashlib, urllib.parse
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
import requests
from cookie_manager import BiliCookiePool

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

OUT = os.path.dirname(os.path.abspath(__file__))
SUB_DIR = os.path.join(OUT, "字幕")
os.makedirs(SUB_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
}

# 精选25个（按相关度打分Top25）
BV_LIST = [
    "BV1zW1bBbEBf", "BV1yw4m1a77W", "BV1mE421A7pH", "BV14B4y167CV", "BV1ni421Y7gQ",
    "BV175MK6iEuf", "BV1uKuRzgEgg", "BV1pA3Sz9EzL", "BV1b11DY5E5h", "BV1gX4y1E7PS",
    "BV1kpbv6LEsm", "BV17whdzEEsF", "BV1ox4y187nd", "BV17yi1B2E9R", "BV1AQKr63EQZ",
    "BV1C2Hi6AEAa", "BV17k4y1S7HW", "BV13S411A7GX", "BV1gZUmYJE6G", "BV1F64y1r79y",
    "BV1zp421o7Yn", "BV1rW4y1m7pk", "BV1dR4y147Pe", "BV1cZ421g7Cg", "BV1VrpE6qEzf",
]

pool = BiliCookiePool()
s = requests.Session()
s.headers.update(HEADERS)
s.headers["Cookie"] = pool.get_cookie()

nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=20).json()
wbi = nav["data"]["wbi_img"]
img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
MIXIN_KEY = "".join((img + sub)[i] for i in MIXIN)[:32]

def sign(p):
    p = dict(p)
    p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q + MIXIN_KEY).encode()).hexdigest()
    return p

def refresh_cookie():
    s.headers["Cookie"] = pool.get_cookie()

results = {}
for bvid in BV_LIST:
    entry = {"bvid": bvid}
    try:
        # 1. 网页HTML取 aid/cid
        r = s.get(f"https://www.bilibili.com/video/{bvid}/", timeout=25)
        t = r.text
        m = (re.search(r"window\.__INITIAL_STATE__=(.*?);\(function", t, re.S)
             or re.search(r"window\.__INITIAL_STATE__=(.*?);\s*</script>", t, re.S))
        v = json.loads(m.group(1))["videoData"]
        aid = v["aid"]
        cid = v["cid"]
        entry["aid"] = aid
        entry["cid"] = cid
        entry["title"] = v.get("title")
        entry["owner"] = (v.get("owner") or {}).get("name")
        entry["duration"] = v.get("duration")
        entry["desc"] = (v.get("desc") or "")[:500]
        time.sleep(1.2)

        # 2. 评论（主评论前3页 + 楼中楼）
        comments = []
        total = 0
        for pn in range(1, 4):
            try:
                rc = s.get("https://api.bilibili.com/x/v2/reply",
                           params={"oid": aid, "type": 1, "pn": pn, "ps": 20, "sort": 2},
                           headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"},
                           timeout=25)
                if rc.status_code == 412 or '"code":-412' in rc.text:
                    pool.report_412(); refresh_cookie(); time.sleep(3); continue
                dd = rc.json().get("data") or {}
                reps = dd.get("replies") or []
                if not reps:
                    break
                pool.report_success()
                if pn == 1:
                    total = (dd.get("page") or {}).get("count", 0)
                for rep in reps:
                    item = {
                        "uname": (rep.get("member") or {}).get("uname"),
                        "like": rep.get("like", 0),
                        "rcount": rep.get("rcount", 0),
                        "message": (rep.get("content") or {}).get("message", ""),
                        "subs": [],
                    }
                    # 楼中楼第1页
                    if rep.get("rcount", 0) > 0:
                        try:
                            r2 = s.get("https://api.bilibili.com/x/v2/reply/reply",
                                       params={"oid": aid, "type": 1, "root": rep.get("rpid"), "pn": 1, "ps": 20},
                                       headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"},
                                       timeout=25)
                            d2 = (r2.json().get("data") or {})
                            for sub_rep in (d2.get("replies") or [])[:10]:
                                item["subs"].append({
                                    "uname": (sub_rep.get("member") or {}).get("uname"),
                                    "like": sub_rep.get("like", 0),
                                    "message": (sub_rep.get("content") or {}).get("message", ""),
                                })
                            time.sleep(0.9)
                        except Exception:
                            pass
                    comments.append(item)
                time.sleep(1.2)
            except Exception as e:
                print(f"  [cmt err] pn{pn}: {e}", flush=True)
                time.sleep(2)
                continue
        entry["comment_total"] = total
        entry["comments"] = comments

        # 3. wbi AI字幕
        sub_ok = False
        for attempt in range(2):
            try:
                q = sign({"bvid": bvid, "cid": str(cid), "web_location": "333.1007"})
                sd = s.get("https://api.bilibili.com/x/player/wbi/v2", params=q,
                           headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"},
                           timeout=20).json()
                subs = ((sd.get("data") or {}).get("subtitle") or {}).get("subtitles") or []
                pick = next((x for pref in ["zh-Hans", "zh-CN", "zh", "ai-zh"] for x in subs if x.get("lan") == pref), None)
                if not pick:
                    break
                u = pick.get("subtitle_url", "")
                if not u:
                    time.sleep(4); continue
                if u.startswith("//"):
                    u = "https:" + u
                body = s.get(u, headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"}, timeout=25).json().get("body", [])
                if body:
                    text = "\n".join(f'[{x.get("from",0):.1f}s] {x.get("content","")}' for x in body)
                    with open(os.path.join(SUB_DIR, f"{bvid}.txt"), "w", encoding="utf-8") as f:
                        f.write(f"# {entry.get('title','')}\n# {bvid}\n\n" + text)
                    entry["subtitle_segs"] = len(body)
                    entry["subtitle_lan"] = pick.get("lan")
                    sub_ok = True
                    break
            except Exception as e:
                print(f"  [sub err]: {e}", flush=True)
                time.sleep(3)
        entry["subtitle_ok"] = sub_ok
        results[bvid] = entry
        print(f"[OK] {bvid} | cmt={len(comments)}/{total} | sub={'Y' if sub_ok else 'N'} | {entry.get('title','')[:30]}", flush=True)
        time.sleep(1.0)
    except Exception as e:
        entry["error"] = str(e)
        results[bvid] = entry
        print(f"[FAIL] {bvid}: {e}", flush=True)
        refresh_cookie()
        time.sleep(3)

with open(os.path.join(OUT, "video_data.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

ok_sub = sum(1 for v in results.values() if v.get("subtitle_ok"))
ok_cmt = sum(1 for v in results.values() if v.get("comments"))
print(f"\nDONE: {len(results)} videos, {ok_cmt} with comments, {ok_sub} with subtitles", flush=True)
