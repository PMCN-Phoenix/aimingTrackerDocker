# -*- coding: utf-8 -*-
"""Step4b: 强制 account3 cookie, 抓字幕"""
import sys, os, time, json, re, hashlib, urllib.parse
import requests

OUT = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q011-跑步速度心率关系\B站原始数据"
COOKIE_FILE = r"D:\11.project\iwen-codex\bilibili-cookies\account3.txt"

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

cookie = open(COOKIE_FILE, encoding="utf-8-sig").read().strip()
s = requests.Session()
s.proxies = {"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Cookie": cookie,
})

nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=20).json()
print(f"[login] {nav['data'].get('uname')} isLogin={nav['data'].get('isLogin')}")
wbi = nav["data"]["wbi_img"]
img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
MIX = "".join((img + sub)[i] for i in MIXIN)[:32]

def sign(p):
    p = dict(p); p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q + MIX).encode()).hexdigest()
    return p

def get_aid_cid(bv):
    r = s.get(f"https://www.bilibili.com/video/{bv}/", timeout=25)
    t = r.text
    m = (re.search(r"window\.__INITIAL_STATE__=(.*?);\(function", t, re.S)
         or re.search(r"window\.__INITIAL_STATE__=(.*?);\s*</script>", t, re.S))
    vd = json.loads(m.group(1))["videoData"]
    return vd.get("aid"), vd.get("cid"), vd.get("duration"), vd.get("title")

def get_sub(bv, cid):
    q = sign({"bvid": bv, "cid": str(cid), "web_location": "333.1007"})
    d = s.get("https://api.bilibili.com/x/player/wbi/v2", params=q,
              headers={"Referer": f"https://www.bilibili.com/video/{bv}/"}, timeout=20).json()
    subs = ((d.get("data") or {}).get("subtitle") or {}).get("subtitles") or []
    return subs

def pick_sub_url(subs):
    for pref in ["zh-Hans", "zh-CN", "zh", "ai-zh"]:
        for x in subs:
            if x.get("lan") == pref:
                return x
    return subs[0] if subs else None

def fmt_ts(sec):
    sec = int(sec); h = sec//3600; m=(sec%3600)//60; ss=sec%60
    return f"{h:d}:{m:02d}:{ss:02d}" if h else f"{m:02d}:{ss:02d}"

sl = json.load(open(os.path.join(OUT, "shortlist.json"), encoding="utf-8"))
results = []
for i, v in enumerate(sl):
    bv = v["bvid"]
    print(f"\n[{i+1}/{len(sl)}] {bv} - {v['title'][:35]}")
    rec = {"bvid": bv, "title": v["title"], "author": v.get("author"),
           "theme": v.get("_theme"), "reason": v.get("_reason")}
    try:
        aid, cid, dur, page_title = get_aid_cid(bv)
        rec["aid"] = aid; rec["cid"] = cid; rec["duration"] = dur
        if not cid:
            rec["status"] = "no_cid"; print("  no cid"); results.append(rec); continue
        time.sleep(1.2)
        # 取字幕列表（重试）
        subs = []
        for attempt in range(3):
            subs = get_sub(bv, cid)
            if subs: break
            time.sleep(2.5)
        rec["sub_langs"] = [x.get("lan") for x in subs]
        if not subs:
            rec["status"] = "no_subtitle"
            print(f"  no AI subtitle (checked 3x)")
            results.append(rec); continue
        pick = pick_sub_url(subs)
        u = pick["subtitle_url"]
        if u.startswith("//"): u = "https:" + u
        body = s.get(u, headers={"Referer": f"https://www.bilibili.com/video/{bv}/"}, timeout=25).json()
        lines = body.get("body") or []
        rec["seg_count"] = len(lines)
        rec["cover_sec"] = lines[-1]["to"] if lines else 0
        rec["status"] = "ok"
        json.dump(body, open(os.path.join(OUT, f"sub_{bv}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        txt = [f"# {v['title']}\n# UP: {v.get('author')}  BV: {bv}\n"]
        for ln in lines:
            txt.append(f"[{fmt_ts(ln['from'])}] {ln['content']}")
        open(os.path.join(OUT, f"txt_{bv}.txt"), "w", encoding="utf-8").write("\n".join(txt))
        print(f"  OK: {len(lines)} segs, cover {fmt_ts(lines[-1]['to'] if lines else 0)}/{dur}")
    except Exception as e:
        rec["status"] = f"error: {e}"
        print(f"  ERR: {e}")
    results.append(rec)
    time.sleep(1.5)

json.dump(results, open(os.path.join(OUT, "subtitle_status.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
ok = sum(1 for r in results if r["status"] == "ok")
print(f"\n[done] {ok}/{len(results)} subtitles OK")
