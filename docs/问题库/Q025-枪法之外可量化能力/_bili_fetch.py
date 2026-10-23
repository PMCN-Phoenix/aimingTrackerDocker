# -*- coding: utf-8 -*-
"""Q025 v2 精选视频：字幕（带时间戳）+ 高赞评论

读取同目录 B站原始数据/精选清单.json（枪法之外可练可量化能力） → 抓取 → 落盘
字幕保存为 [mm:ss] 文本，便于报告里做「bvid + 时间戳」引用。
评论走 legacy /x/v2/reply（wbi/main 会 -403），失败回退 wbi/main。
"""
import sys, json, time, os, re, requests, hashlib, urllib.parse

sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "B站原始数据")
SUB_DIR = os.path.join(RAW, "字幕")
os.makedirs(SUB_DIR, exist_ok=True)

with open(os.path.join(RAW, "精选清单.json"), encoding="utf-8") as f:
    PICKS = [(x["bvid"], x["name"]) for x in json.load(f)]

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

def wbi_params(params):
    c = pool.get_cookie()
    s.headers["Cookie"] = c
    nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=15).json()
    wbi = nav["data"]["wbi_img"]
    img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
    mk = "".join((img + sub)[i] for i in MIXIN)[:32]
    params["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(params.items()))
    params["w_rid"] = hashlib.md5((q + mk).encode()).hexdigest()
    return params

def get_cid(bvid):
    s.headers["Cookie"] = pool.get_cookie()
    j = s.get("https://api.bilibili.com/x/player/pagelist", params={"bvid": bvid}, timeout=20).json()
    if j.get("code") == 0 and j.get("data"):
        return j["data"][0]["cid"]
    return None

def fmt(t):
    t = int(t or 0)
    return f"{t // 60:02d}:{t % 60:02d}"

def get_subtitle(bvid, cid):
    s.headers["Cookie"] = pool.get_cookie()
    p = wbi_params({"bvid": bvid, "cid": cid})
    j = s.get("https://api.bilibili.com/x/player/wbi/v2", params=p, timeout=20).json()
    if j.get("code") != 0:
        return None, f"code={j.get('code')}"
    subs = (j.get("data", {}).get("subtitle", {}) or {}).get("subtitles", [])
    if not subs:
        return None, "no-subtitle"
    subs.sort(key=lambda x: 0 if "ai" in (x.get("lan") or "") else 1)
    url = subs[0].get("subtitle_url") or ""
    if url.startswith("//"):
        url = "https:" + url
    if not url:
        return None, "empty-url"
    rr = requests.get(url, timeout=20, headers={"User-Agent": s.headers["User-Agent"]})
    try:
        body = rr.json().get("body", [])
    except Exception:
        return None, "json-fail"
    lines = [f"[{fmt(b.get('from'))}] {b.get('content', '')}" for b in body]
    return "\n".join(lines), f"{len(lines)} lines"

def get_comments(bvid, limit_pages=2):
    s.headers["Cookie"] = pool.get_cookie()
    v = s.get("https://api.bilibili.com/x/web-interface/view", params={"bvid": bvid}, timeout=20).json()
    if v.get("code") != 0:
        return None, f"view code={v.get('code')}"
    aid = v["data"]["aid"]
    rows = []
    total = 0
    for pn in range(1, limit_pages + 1):
        params = {"oid": aid, "type": 1, "pn": pn, "ps": 20, "sort": 2}
        r = s.get("https://api.bilibili.com/x/v2/reply", params=params, timeout=25)
        if r.status_code == 412 or '"code":-412' in r.text:
            pool.report_412()
            break
        j = r.json()
        if j.get("code") != 0:
            # 回退 wbi/main
            p2 = wbi_params({"oid": aid, "type": 1, "pn": pn, "ps": 20, "sort": 2})
            j = s.get("https://api.bilibili.com/x/v2/reply/wbi/main", params=p2, timeout=25).json()
            if j.get("code") != 0:
                break
        data = j.get("data") or {}
        total = (data.get("page") or {}).get("count", total) or total
        for c in (data.get("replies") or []):
            rows.append({
                "uname": c["member"]["uname"],
                "like": c["like"],
                "message": c["content"]["message"],
                "subs": [{"uname": x["member"]["uname"], "like": x["like"],
                          "message": x["content"]["message"]} for x in (c.get("replies") or [])][:5],
            })
        time.sleep(1.2)
    return {"aid": aid, "count": total, "comments": rows}, f"顶层{len(rows)}条/总{total}"

ok_sub = ok_cmt = 0
cmt_all = {}
for bvid, name in PICKS:
    try:
        cid = get_cid(bvid)
        time.sleep(0.6)
        if cid:
            txt, info = get_subtitle(bvid, cid)
            if txt:
                safe = re.sub(r'[\\/:*?"<>|]', "_", name)[:60]
                with open(os.path.join(SUB_DIR, f"{safe}__{bvid}.txt"), "w", encoding="utf-8") as f:
                    f.write(txt)
                print(f"[字幕OK] {name[:28]} ({bvid}) {info}")
                ok_sub += 1
            else:
                print(f"[无字幕] {name[:28]} ({bvid}) {info}")
        else:
            print(f"[无cid] {name[:28]} ({bvid})")
        time.sleep(1.0)
        cm, cinfo = get_comments(bvid)
        if cm:
            cmt_all[bvid] = {"title": name, **cm}
            print(f"[评论OK] {bvid} {cinfo}")
            ok_cmt += 1
        else:
            print(f"[评论失败] {bvid} {cinfo}")
    except Exception as e:
        print(f"[错误] {bvid} {str(e)[:90]}")
    time.sleep(1.4)

with open(os.path.join(RAW, "评论.json"), "w", encoding="utf-8") as f:
    json.dump(cmt_all, f, ensure_ascii=False, indent=1)

print(f"\n字幕成功 {ok_sub}/{len(PICKS)}｜评论成功 {ok_cmt}/{len(PICKS)}")
