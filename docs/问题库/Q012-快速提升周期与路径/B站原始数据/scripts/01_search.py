# -*- coding: utf-8 -*-
"""
Q012 B站调研 - 第1步：9组关键词搜索
输出：B站原始数据/搜索结果.json
"""
import sys, os, time, json, re, hashlib, urllib.parse, requests
from pathlib import Path

# 引入cookie池
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q012-快速提升周期与路径\B站原始数据")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

KEYWORDS = [
    # 主题A：上分周期/段位提升时间
    ("A", "无畏契约 上分周期 多久"),
    ("A", "VALORANT 段位提升 时间"),
    ("A", "瓦罗兰特 从黄金到钻石 要多久"),
    # 主题B：快速提升/训练方法论
    ("B", "无畏契约 快速提升 方法"),
    ("B", "VALORANT 训练计划 上分效率"),
    ("B", "瓦罗兰特 瓶颈突破 卡段位"),
    # 主题C：意识/复盘/训练结构
    ("C", "无畏契约 复盘方法 提升"),
    ("C", "VALORANT 意识提升 大局观"),
    ("C", "瓦罗兰特 每天训练安排 时间分配"),
]

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"


def make_session(cookie_str):
    s = requests.Session()
    s.headers.update({
        "User-Agent": UA,
        "Referer": "https://search.bilibili.com/",
    })
    # 解析cookie到session
    for part in cookie_str.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            s.cookies.set(k.strip().lstrip("\ufeff"), v.strip())
    return s


def get_wbi_keys(s):
    r = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=20).json()
    wbi = r["data"]["wbi_img"]
    img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
    return "".join((img + sub)[i] for i in MIXIN)[:32]


def sign(params, mixin):
    p = dict(params)
    p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q + mixin).encode()).hexdigest()
    return p


def clean_title(t):
    return re.sub(r"<[^>]+>", "", t or "")


def main():
    pool = BiliCookiePool()
    print(pool.status())

    all_videos = {}  # bvid -> record
    stats = {"total_raw": 0, "per_keyword": []}

    for theme, kw in KEYWORDS:
        print(f"\n=== [{theme}] 搜索: {kw} ===")
        cookie = pool.get_cookie()
        s = make_session(cookie)
        try:
            mixin = get_wbi_keys(s)
        except Exception as e:
            print(f"  获取wbi keys失败: {e}, 切换cookie")
            pool.report_412()
            cookie = pool.get_cookie()
            s = make_session(cookie)
            mixin = get_wbi_keys(s)

        got = 0
        for page in (1, 2):  # 2页 x 30条 = 60条/关键词
            params = {
                "search_type": "video",
                "keyword": kw,
                "page": page,
                "page_size": 30,
                "order": "totalrank",
            }
            signed = sign(params, mixin)
            try:
                r = s.get("https://api.bilibili.com/x/web-interface/wbi/search/type",
                          params=signed, timeout=25)
                d = r.json()
            except Exception as e:
                print(f"  page{page} 请求异常: {e}")
                time.sleep(2)
                continue

            if d.get("code") != 0:
                print(f"  page{page} code={d.get('code')} msg={d.get('message')}")
                if d.get("code") in (-412, -799):
                    pool.report_412()
                time.sleep(3)
                continue

            results = (d.get("data") or {}).get("result") or []
            if not results:
                break

            for v in results:
                if v.get("type") != "video":
                    continue
                bvid = v.get("bvid")
                if not bvid:
                    continue
                stats["total_raw"] += 1
                got += 1
                rec = {
                    "bvid": bvid,
                    "title": clean_title(v.get("title")),
                    "author": v.get("author", ""),
                    "mid": v.get("mid", 0),
                    "play": v.get("play", 0),
                    "danmaku": v.get("video_review", 0),
                    "favorites": v.get("favorites", 0),
                    "reply": v.get("review", 0),
                    "duration": v.get("duration", ""),  # "mm:ss"
                    "pubdate": v.get("pubdate", 0),
                    "description": clean_title(v.get("description", "")),
                    "keyword_hit": theme,
                    "source_keyword": kw,
                }
                if bvid not in all_videos:
                    all_videos[bvid] = rec
                else:
                    # 记录被哪些关键词命中
                    all_videos[bvid]["hit_themes"] = list(
                        set(all_videos[bvid].get("hit_themes", [all_videos[bvid]["keyword_hit"]]) + [theme])
                    )
                    all_videos[bvid]["hit_keywords"] = list(
                        set(all_videos[bvid].get("hit_keywords", [all_videos[bvid]["source_keyword"]]) + [kw])
                    )
            pool.report_success()
            time.sleep(1.5)

        stats["per_keyword"].append({"keyword": kw, "theme": theme, "got": got})
        print(f"  本关键词新增: {got} (累计去重后: {len(all_videos)})")
        time.sleep(2)

    # 保存
    out = {
        "search_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "stats": stats,
        "videos": list(all_videos.values()),
    }
    out_path = OUT_DIR / "搜索结果.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n=== 完成 ===")
    print(f"原始条数: {stats['total_raw']}")
    print(f"去重后: {len(all_videos)}")
    print(f"已保存: {out_path}")


if __name__ == "__main__":
    main()
