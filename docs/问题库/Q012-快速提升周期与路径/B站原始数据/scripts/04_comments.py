# -*- coding: utf-8 -*-
"""
Q012 B站调研 - 第4步：抓最高播放3个视频的主评论（前20条）
输出：评论.json
"""
import sys, os, time, json, requests
from pathlib import Path

sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q012-快速提升周期与路径\B站原始数据")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"

# 最高播放3个视频（从精选列表里选）
TARGETS = [
    ("BV1tButzYE8d", 114861400924127),  # 841k 赋能3分钟练枪
    ("BV19XzHYsEdy", 113572558542748),  # 759k 上超凡做好几点
    ("BV1ga37zyETR", 114794107508960),  # 203k 300小时上超凡
]


def make_session(cookie_str):
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    for part in cookie_str.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            s.cookies.set(k.strip().lstrip("\ufeff"), v.strip())
    return s


def fetch_main_comments(bvid, aid, s, pool, max_items=20):
    """抓主评论（热度排序）"""
    comments = []
    for pn in range(1, 3):
        try:
            r = s.get("https://api.bilibili.com/x/v2/reply",
                      params={"oid": aid, "type": 1, "pn": pn, "ps": 20, "sort": 2},
                      headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"},
                      timeout=25)
            d = r.json()
        except Exception as e:
            print(f"    pn{pn} 异常: {e}")
            pool.report_412()
            time.sleep(3)
            break

        if d.get("code") != 0:
            print(f"    pn{pn} code={d.get('code')} msg={d.get('message')}")
            pool.report_412()
            break

        dd = d.get("data") or {}
        reps = dd.get("replies") or []
        if not reps:
            break

        for rep in reps:
            content = rep.get("content", {})
            comments.append({
                "uname": rep.get("member", {}).get("uname", ""),
                "like": rep.get("like", 0),
                "rcount": rep.get("rcount", 0),
                "message": content.get("message", ""),
                "ctime": rep.get("ctime", 0),
            })
            if len(comments) >= max_items:
                break
        if len(comments) >= max_items:
            break
        time.sleep(1.2)

    pool.report_success()
    return comments


def main():
    pool = BiliCookiePool()
    result = {}

    for bvid, aid in TARGETS:
        print(f"=== {bvid} (aid={aid}) ===")
        cookie = pool.get_cookie()
        s = make_session(cookie)
        comments = fetch_main_comments(bvid, aid, s, pool)
        print(f"  抓到 {len(comments)} 条评论")
        result[bvid] = {
            "aid": aid,
            "count": len(comments),
            "comments": comments,
        }
        time.sleep(2)

    out_path = OUT_DIR / "评论.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已保存: {out_path}")
    for bvid, r in result.items():
        print(f"  {bvid}: {r['count']} 条")


if __name__ == "__main__":
    main()
