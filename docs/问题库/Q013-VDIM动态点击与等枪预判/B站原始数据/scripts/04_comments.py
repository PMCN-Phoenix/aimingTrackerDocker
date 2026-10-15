# -*- coding: utf-8 -*-
"""Q013 抓核心视频评论"""
import sys, time, json, requests
from pathlib import Path

sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

OUT = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\B站原始数据")
CMT_DIR = OUT / "comments"
CMT_DIR.mkdir(exist_ok=True)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"

# 需要先拿aid，用search结果里的mid不够，得从字幕json里拿
TARGETS = [
    "BV1zUjY6iEzs",   # 时停tt 用眼方法论
    "BV1eehiz9EEc",   # 晨曜 动态定位
    "BV1UV4y1k76r",   # Sondo301 开枪太急
    "BV1ecbAznETh",   # Kovaak 手抖
    "BV1C2Hi6AEAa",   # 晨曜 微调（复用）
]


def make_session(c):
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    for p in c.split(";"):
        p = p.strip()
        if "=" in p:
            k, v = p.split("=", 1)
            s.cookies.set(k.strip().lstrip("\ufeff"), v.strip())
    return s


def get_aid(bvid, s):
    """从字幕json读aid，没有就抓网页"""
    jp = OUT / "subtitles" / f"{bvid}.json"
    if jp.exists():
        j = json.load(open(jp, encoding="utf-8"))
        if j.get("aid"):
            return j["aid"]
    # 抓网页
    import re
    r = s.get(f"https://www.bilibili.com/video/{bvid}/",
              headers={"Referer": "https://www.bilibili.com/"}, timeout=25)
    m = re.search(r'"aid":(\d+)', r.text)
    return int(m.group(1)) if m else None


def fetch_comments(bvid, aid, s, pool, max_items=30):
    comments = []
    for pn in range(1, 3):
        try:
            r = s.get("https://api.bilibili.com/x/v2/reply",
                      params={"oid": aid, "type": 1, "pn": pn, "ps": 20, "sort": 2},
                      headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"},
                      timeout=25)
            d = r.json()
        except Exception as e:
            print(f"    pn{pn} 异常 {e}")
            pool.report_412(); time.sleep(3); break
        if d.get("code") != 0:
            print(f"    pn{pn} code={d.get('code')} msg={d.get('message')}")
            pool.report_412(); break
        reps = (d.get("data") or {}).get("replies") or []
        if not reps: break
        for rep in reps:
            comments.append({
                "uname": rep.get("member", {}).get("uname", ""),
                "like": rep.get("like", 0),
                "message": rep.get("content", {}).get("message", ""),
            })
            if len(comments) >= max_items: break
        if len(comments) >= max_items: break
        time.sleep(1.2)
    pool.report_success()
    return comments


def main():
    pool = BiliCookiePool()
    result = {}
    for bvid in TARGETS:
        print(f"=== {bvid} ===")
        s = make_session(pool.get_cookie())
        aid = get_aid(bvid, s)
        if not aid:
            print("  拿不到aid"); continue
        print(f"  aid={aid}, 抓评论...")
        cmts = fetch_comments(bvid, aid, s, pool)
        print(f"  抓到 {len(cmts)} 条")
        result[bvid] = {"aid": aid, "count": len(cmts), "comments": cmts}
        time.sleep(2)
    (CMT_DIR / "comments.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n保存到 {CMT_DIR / 'comments.json'}")


if __name__ == "__main__":
    main()
