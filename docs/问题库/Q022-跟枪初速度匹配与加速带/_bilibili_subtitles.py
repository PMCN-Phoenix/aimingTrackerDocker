# -*- coding: utf-8 -*-
"""B站字幕抓取：Q022 跟枪初速度匹配与加速带"""
import sys, json, time, requests, re, os
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

SELECTED = [
    ("BV1wrJJ61EAc", "中距离瞄准秘籍 移动目标提前量教学"),
    ("BV1mb4y1i7CW", "细说平滑和变向在跟枪中的差别"),
    ("BV18Sje6REjx", "兼具平滑跟枪与精准定位的固定加速度值"),
    ("BV1Wj411z7cb", "APEX敌人左右变向打不中 跟枪不平滑"),
    ("BV1EZ4y1m7EA", "跟枪不平滑 为什么我停枪时会抖"),
    ("BV1pNGWznERv", "如何在任何游戏中都完美的跟枪"),
    ("BV1tNj86uET6", "平滑跟枪的秘诀"),
    ("BV1654y1d73x", "跟枪不是无数次的定位 如何成为跟枪锁子哥"),
    ("BV1654y1a7hD", "提前预判枪在实战中究竟有多强"),
    ("BV1ox4y187nd", "跟枪学习完全攻略指南"),
    ("BV1oMfGBrEGg", "从本质出发系统性训练跟枪"),
    ("BV17V411g7Ht", "纯反应力 vs 反应跟枪"),
    ("BV1dEeUzPEGk", "为什么你的跟枪瞄准需要这种训练方法"),
    ("BV1o54y1R732", "世界前一百的跟枪是怎么练成的"),
    ("BV1fsua6mEDD", "理工科博士生 理论拆解FPS瞄准 为什么鼠标会卡住"),
    ("BV1xeN76rECh", "只练一次定位会毁了你的瞄准 跟枪"),
    ("BV13W5u6UEEQ", "一分钟教会你练习移动跟枪的动态瞄准"),
    ("BV1PHhB6hEqh", "进阶FPS视觉训练 提升跟枪能力与反应速度"),
]


def get_cid(bvid):
    r = s.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", timeout=20).json()
    if r.get("code") != 0:
        return None, r.get("message")
    return r["data"]["cid"], None


def get_subtitle_url(bvid, cid):
    r = s.get(f"https://api.bilibili.com/x/player/wbi/v2?bvid={bvid}&cid={cid}", timeout=20).json()
    subs = r.get("data", {}).get("subtitle", {}).get("subtitles", [])
    if not subs:
        return None
    subs.sort(key=lambda x: 0 if "zh" in x.get("lan", "") else 1)
    return subs[0].get("subtitle_url", "")


def fetch_subtitle(url):
    if url.startswith("//"):
        url = "https:" + url
    r = s.get(url, timeout=20).json()
    return "\n".join(item["content"] for item in r.get("body", []))


out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "B站原始数据", "字幕")
os.makedirs(out_dir, exist_ok=True)
ok, fail = 0, []
for bvid, title in SELECTED:
    safe = re.sub(r'[\\/:*?"<>|]', "_", title)[:60]
    path = os.path.join(out_dir, f"{bvid}_{safe}.txt")
    if os.path.exists(path):
        print(f"  已存在: {bvid}")
        ok += 1
        continue
    try:
        s.headers["Cookie"] = pool.get_cookie()
        cid, err = get_cid(bvid)
        if not cid:
            fail.append(f"{bvid} {err}")
            print(f"  cid失败: {bvid} {err}")
            continue
        url = get_subtitle_url(bvid, cid)
        if not url:
            fail.append(f"{bvid} 无字幕")
            print(f"  无字幕: {bvid} {title[:30]}")
            continue
        text = fetch_subtitle(url)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n# {bvid}\n\n" + text)
        ok += 1
        print(f"  OK: {bvid} {title[:36]} ({len(text)}字)")
    except Exception as e:
        fail.append(f"{bvid} {e}")
        print(f"  错误: {bvid} {e}")
    time.sleep(1.5)

print(f"\n完成 {ok}/{len(SELECTED)}，失败: {len(fail)}")
for f_ in fail:
    print(f"  - {f_}")
