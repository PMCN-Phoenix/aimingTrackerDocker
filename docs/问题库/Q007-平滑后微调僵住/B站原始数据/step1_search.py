# -*- coding: utf-8 -*-
"""
Step1: 多关键词搜索 + 去重 + 打分
输出: 搜索清单JSON
"""
import sys, os, re, json, time, hashlib, urllib.parse
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool
import requests

OUT_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q007-平滑后微调僵住\B站原始数据"
os.makedirs(OUT_DIR, exist_ok=True)

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

PROXIES = {"http": "http://127.0.0.1:7892", "https": "http://127.0.0.1:7892"}

KEYWORDS = [
    "平滑跟枪 微调 切换",
    "手臂瞄准 手腕微调 过渡",
    "瞄准 僵住 动不了 张力",
    "鼠标控制 精细度 微定位",
    "palm grip 趴握 微调 精准",
    "微调甜蜜区 减速确认",
    "手指微调 握法 三指捏鼠",
    "瞄准放松 张力 卸力",
    # 补充英文/换说法
    "aim 手臂流 手腕流 切换",
    "跟枪 急停 微调 枪法",
    "kovaak 平滑 微调 训练",
    "FPS 瞄准 放松 握鼠标",
]

def clean_html(t):
    return re.sub(r"<[^>]+>", "", t or "")

def make_session(pool):
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
    })
    s.proxies.update(PROXIES)
    s.headers["Cookie"] = pool.get_cookie()
    return s

def get_wbi_keys(s):
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

def search_one(s, mixin, kw, pool, page=1):
    p = sign({"search_type": "video", "keyword": kw, "page": page, "page_size": 30}, mixin)
    for attempt in range(3):
        try:
            r = s.get("https://api.bilibili.com/x/web-interface/wbi/search/type",
                      params=p, timeout=25)
            d = r.json()
            if d.get("code") == 0:
                pool.report_success()
                return d.get("data") or {}
            if d.get("code") == -412:
                pool.report_412()
                s.headers["Cookie"] = pool.get_cookie()
                time.sleep(3)
                continue
            # 其他错误
            print(f"  [!] code={d.get('code')} msg={d.get('message')}")
            time.sleep(2)
        except Exception as e:
            print(f"  [!] exception: {e}")
            time.sleep(3)
    return {}

def duration_to_sec(dur):
    # "mm:ss" or "hh:mm:ss"
    parts = dur.split(":")
    try:
        if len(parts) == 2:
            return int(parts[0])*60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
    except:
        return 0
    return 0

def score_video(v):
    t = (v.get("title") or "") + " " + (v.get("description") or "")
    t_low = t.lower()
    s = 0.0
    # 主题相关词权重
    weights = [
        ("微调", 5), ("微定位", 5), ("精细", 4), ("精准", 3),
        ("手臂", 3), ("手腕", 3), ("手指", 2), ("握法", 3), ("趴握", 4), ("palm", 4),
        ("僵", 4), ("张力", 4), ("放松", 3), ("卸力", 3), ("紧张", 2),
        ("平滑", 3), ("跟枪", 3), ("追踪", 2), ("tracking", 3),
        ("切换", 4), ("过渡", 3), ("甜蜜区", 4), ("减速", 3),
        ("急停", 3), ("急停定位", 4), ("定位", 2),
        ("kovaak", 3), ("aimlab", 3), ("aim lab", 3), ("瞄准", 2),
        ("fps", 1), ("枪法", 2), ("练枪", 2),
        ("手臂流", 4), ("手腕流", 4),
    ]
    for kw, w in weights:
        if kw.lower() in t_low:
            s += w
    # 播放量
    play = v.get("play") or 0
    if play > 500000: s += 4
    elif play > 100000: s += 3
    elif play > 50000: s += 2
    elif play > 10000: s += 0.5
    elif play < 1000: s -= 2
    # 时长
    dur_s = v.get("_dur_s", 0)
    if dur_s < 60: s -= 1.5
    if dur_s > 1800: s += 1  # 长视频信息多
    return s

def main():
    pool = BiliCookiePool()
    print(pool.status())
    s = make_session(pool)
    mixin = get_wbi_keys(s)
    print(f"[OK] wbi mixin={mixin[:8]}...")

    all_videos = {}  # bvid -> video dict
    for kw in KEYWORDS:
        print(f"\n=== 搜索: {kw} ===")
        data = search_one(s, mixin, kw, pool, page=1)
        results = data.get("result") or []
        # 过滤掉非视频(可能有用户/番剧)
        cnt_new = 0
        for v in results:
            if v.get("type") and v["type"] != "video":
                continue
            bvid = v.get("bvid")
            if not bvid:
                continue
            title = clean_html(v.get("title"))
            dur = v.get("duration") or ""
            item = {
                "bvid": bvid,
                "title": title,
                "author": v.get("author"),
                "play": v.get("play"),
                "duration": dur,
                "_dur_s": duration_to_sec(dur),
                "description": clean_html(v.get("description") or ""),
                "pubdate": v.get("pubdate"),
                "tag": v.get("tag", ""),
                "search_kw": [kw],
            }
            if bvid in all_videos:
                all_videos[bvid]["search_kw"].append(kw)
                # 合并标题/描述中更长的
                if len(item["description"]) > len(all_videos[bvid]["description"]):
                    all_videos[bvid]["description"] = item["description"]
            else:
                all_videos[bvid] = item
                cnt_new += 1
        print(f"  本页 {len(results)} 条, 新增 {cnt_new}, 累计 {len(all_videos)}")
        time.sleep(1.5)

    # 打分
    for bvid, v in all_videos.items():
        v["score"] = score_video(v)

    # 按分数排序
    ranked = sorted(all_videos.values(), key=lambda x: -x["score"])

    out_path = os.path.join(OUT_DIR, "搜索清单.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(ranked, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] 共 {len(ranked)} 个去重视频, 已保存到 {out_path}")

    # 打印 top 60 供精选
    print("\n=== Top 60 候选 ===")
    for i, v in enumerate(ranked[:60]):
        print(f"{i+1:2d}. [{v['score']:5.1f}] {v['bvid']} | 播放{v.get('play'):>8} | {v['duration']:>8} | {v['author'][:12]:<12} | {v['title'][:50]}")

if __name__ == "__main__":
    main()
