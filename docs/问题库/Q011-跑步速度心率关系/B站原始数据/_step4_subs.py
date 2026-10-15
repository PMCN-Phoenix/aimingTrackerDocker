# -*- coding: utf-8 -*-
"""Step4: 对 shortlist 视频, 抓 aid/cid (HTML __INITIAL_STATE__) -> wbi 字幕 -> 落盘"""
import sys, os, time, json, re, hashlib, urllib.parse
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool
import requests

OUT = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q011-跑步速度心率关系\B站原始数据"

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

def make_session():
    s = requests.Session()
    s.proxies = {"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    })
    pool = BiliCookiePool()
    s.headers["Cookie"] = pool.get_cookie()
    return s, pool

def get_wbi_mixin(s):
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

def get_aid_cid(s, bvid):
    """抓视频页 HTML, 正则取 __INITIAL_STATE__"""
    url = f"https://www.bilibili.com/video/{bvid}/"
    r = s.get(url, timeout=25)
    t = r.text
    m = (re.search(r"window\.__INITIAL_STATE__=(.*?);\(function", t, re.S)
         or re.search(r"window\.__INITIAL_STATE__=(.*?);\s*</script>", t, re.S))
    if not m:
        return None, None, None
    try:
        vd = json.loads(m.group(1))["videoData"]
    except Exception as e:
        print(f"    [parse err] {e}")
        return None, None, None
    aid = vd.get("aid")
    cid = vd.get("cid")
    title = vd.get("title")
    pages = vd.get("pages") or []
    return aid, cid, {"title": title, "pages": pages, "duration": vd.get("duration")}

def get_subtitle(s, bvid, cid, mixin):
    q = sign({"bvid": bvid, "cid": str(cid), "web_location": "333.1007"}, mixin)
    d = s.get("https://api.bilibili.com/x/player/wbi/v2", params=q,
              headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"}, timeout=20).json()
    subs = ((d.get("data") or {}).get("subtitle") or {}).get("subtitles") or []
    if not subs:
        return None, subs
    # 语言优先级
    pick = None
    for pref in ["zh-Hans", "zh-CN", "zh", "ai-zh"]:
        for x in subs:
            if x.get("lan") == pref:
                pick = x; break
        if pick: break
    if not pick:
        pick = subs[0]
    u = pick.get("subtitle_url") or ""
    if not u:
        return None, subs
    if u.startswith("//"):
        u = "https:" + u
    body = s.get(u, headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"}, timeout=25).json()
    return body, subs

def fmt_ts(sec):
    sec = int(sec)
    h = sec // 3600; m = (sec % 3600) // 60; s = sec % 60
    if h: return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def main():
    sl = json.load(open(os.path.join(OUT, "shortlist.json"), encoding="utf-8"))
    s, pool = make_session()
    mixin = get_wbi_mixin(s)
    print(f"[mixin] ok, {len(sl)} videos to process")

    results = []
    for i, v in enumerate(sl):
        bv = v["bvid"]
        print(f"\n[{i+1}/{len(sl)}] {bv} - {v['title'][:40]}")
        rec = {"bvid": bv, "title": v["title"], "author": v.get("author"),
               "theme": v.get("_theme"), "reason": v.get("_reason")}
        try:
            aid, cid, meta = get_aid_cid(s, bv)
            rec["aid"] = aid
            rec["cid"] = cid
            if not cid:
                rec["status"] = "no_cid"
                print("  no cid")
                results.append(rec); continue
            print(f"  aid={aid} cid={cid}")
            time.sleep(1.2)

            # 字幕（重试4次）
            body, subs = None, []
            for attempt in range(4):
                body, subs = get_subtitle(s, bv, cid, mixin)
                if body and body.get("body"):
                    break
                print(f"  subtitle empty, retry {attempt+1}/4...")
                time.sleep(3)
            rec["sub_lan_list"] = [x.get("lan") for x in subs]
            if not body or not body.get("body"):
                rec["status"] = "no_subtitle"
                print(f"  no AI subtitle (langs seen: {rec['sub_lan_list']})")
                results.append(rec); continue

            lines = body["body"]
            rec["seg_count"] = len(lines)
            rec["cover_sec"] = lines[-1].get("to", 0)
            rec["duration"] = meta.get("duration") if meta else None
            rec["status"] = "ok"

            # 存原始 JSON
            with open(os.path.join(OUT, f"sub_{bv}.json"), "w", encoding="utf-8") as f:
                json.dump(body, f, ensure_ascii=False, indent=2)
            # 存纯文本（带时间戳）
            txt_lines = [f"# {v['title']}\n# UP: {v.get('author')}  BV: {bv}\n"]
            for ln in lines:
                txt_lines.append(f"[{fmt_ts(ln['from'])}] {ln['content']}")
            with open(os.path.join(OUT, f"txt_{bv}.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join(txt_lines))
            print(f"  subtitle OK: {len(lines)} segs, cover {fmt_ts(lines[-1]['to'])} / {meta.get('duration') if meta else '?'}")
        except Exception as e:
            rec["status"] = f"error: {e}"
            print(f"  ERROR: {e}")
        results.append(rec)
        time.sleep(1.5)

    with open(os.path.join(OUT, "subtitle_status.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"\n[done] {ok}/{len(results)} subtitles OK")

if __name__ == "__main__":
    main()
