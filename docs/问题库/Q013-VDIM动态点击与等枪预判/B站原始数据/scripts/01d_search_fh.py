# -*- coding: utf-8 -*-
"""Q013 追加搜索2：Floating Heads Timing"""
import sys, time, json, re, hashlib, urllib.parse, requests
from pathlib import Path

sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

OUT = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\B站原始数据")

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

KEYWORDS = [
    ("D5", "Floating Heads Timing 训练"),
    ("D5", "Kovaak Floating Heads 技巧"),
    ("D5", "Floating Heads 400% 分数"),
    ("D5", "漂浮人头 瞄准 时机"),
    ("D5", "VDIM Floating Heads Timing"),
]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"


def make_session(c):
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Referer": "https://search.bilibili.com/"})
    for p in c.split(";"):
        p = p.strip()
        if "=" in p:
            k, v = p.split("=", 1)
            s.cookies.set(k.strip().lstrip("\ufeff"), v.strip())
    return s


def wbi_keys(s):
    r = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=20).json()
    w = r["data"]["wbi_img"]
    img = w["img_url"].rsplit("/", 1)[-1].split(".")[0]
    sub = w["sub_url"].rsplit("/", 1)[-1].split(".")[0]
    return "".join((img + sub)[i] for i in MIXIN)[:32]


def sign(p, m):
    p = dict(p); p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q + m).encode()).hexdigest()
    return p


def clean(t):
    return re.sub(r"<[^>]+>", "", t or "")


def main():
    pool = BiliCookiePool()
    existing = json.load(open(OUT / "search_results.json", encoding="utf-8"))
    all_v = {v["bvid"]: v for v in existing["videos"]}
    print(f"已有 {len(all_v)}")

    for theme, kw in KEYWORDS:
        print(f"\n=== [{theme}] {kw} ===")
        s = make_session(pool.get_cookie())
        try:
            m = wbi_keys(s)
        except Exception:
            pool.report_412(); s = make_session(pool.get_cookie()); m = wbi_keys(s)
        got = 0
        for page in (1, 2):
            params = {"search_type": "video", "keyword": kw, "page": page,
                      "page_size": 30, "order": "totalrank"}
            try:
                r = s.get("https://api.bilibili.com/x/web-interface/wbi/search/type",
                          params=sign(params, m), timeout=25)
                d = r.json()
            except Exception as e:
                print(f"  p{page} 异常 {e}"); time.sleep(2); continue
            if d.get("code") != 0:
                print(f"  p{page} code={d.get('code')}")
                if d.get("code") in (-412, -799): pool.report_412()
                time.sleep(3); continue
            results = (d.get("data") or {}).get("result") or []
            if not results: break
            for v in results:
                if v.get("type") != "video": continue
                bv = v.get("bvid")
                if not bv: continue
                got += 1
                rec = {"bvid": bv, "title": clean(v.get("title")), "author": v.get("author",""),
                       "mid": v.get("mid",0), "play": v.get("play",0),
                       "danmaku": v.get("video_review",0), "favorites": v.get("favorites",0),
                       "reply": v.get("review",0), "duration": v.get("duration",""),
                       "pubdate": v.get("pubdate",0),
                       "description": clean(v.get("description","")),
                       "keyword_hit": theme, "source_keyword": kw}
                if bv not in all_v:
                    all_v[bv] = rec
                else:
                    old = all_v[bv]
                    old["hit_themes"] = list(set(old.get("hit_themes",[old.get("keyword_hit","")])+[theme]))
                    old["hit_keywords"] = list(set(old.get("hit_keywords",[old.get("source_keyword","")])+[kw]))
            pool.report_success(); time.sleep(1.5)
        existing["stats"]["per_keyword"].append({"keyword": kw, "theme": theme, "got": got})
        print(f"  got={got}, 累计={len(all_v)}")
        time.sleep(2)

    existing["videos"] = list(all_v.values())
    existing["stats"]["total_raw"] = sum(p["got"] for p in existing["stats"]["per_keyword"])
    existing["stats"]["fh_search_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    (OUT / "search_results.json").write_text(
        json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n合并后总数: {len(all_v)}")


if __name__ == "__main__":
    main()
