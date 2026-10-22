# -*- coding: utf-8 -*-
"""B站字幕抓取：Q024 练枪迁移实战 + 紧张失能"""
import sys, json, time, requests, re, os
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

SELECTED = [
    ("BV1gSjV6NEg1", "付费挨骂 练枪实战发挥不出来才是常态 没有思路就会犹犹豫豫"),
    ("BV15L411p7oi", "练枪软件到底有什么用 为什么越练枪实战反而越拉胯"),
    ("BV1te4y1x7EC", "为什么练枪软件无法提高实战 缺点局限性与正确使用方式"),
    ("BV1q7tX6UEH4", "练枪很久但没有效果 练枪软件分数实战不转化"),
    ("BV1m14y1q7rX", "练枪软件瞄准能力与游戏枪法之间的转化效率"),
    ("BV1YG411f7R3", "死斗练枪注重预瞄 实战不要刻意注意 凭感觉打"),
    ("BV1S4K56kEUW", "心态脱敏帮你摆脱实战心跳加速紧张手抖"),
    ("BV1L8mEBaEsA", "关键局压力暴增导致手抖失误 教你如何快速调整心态"),
    ("BV1yETY6REQB", "一对枪就害怕 学会控制心态才能发挥你的真实水平"),
    ("BV1UZm4B5EoF", "FPS游戏遇到人就紧张手抖 一个视频告诉你该怎么办"),
    ("BV1W4411H7io", "如何在激烈的电子游戏中避免紧张克服手抖"),
    ("BV1rcuh6LEvk", "一看到人就紧张乱开枪 这个练习能救你"),
    ("BV1mH4y1L7VK", "TED 比赛紧张 揭秘如何克服压力下的窒息"),
    ("BV12p411o7oh", "怎样在紧张时停止颤抖"),
    ("BV1h94y1v7Th", "为什么拉伸往往无法缓解紧张的肌肉"),
    ("BV1xSRDBWE3P", "实战瞄准发挥不出来 那你非常需要学这期的技巧"),
    ("BV1bj411Q7bw", "紧张到手抖 揭秘压力背后的生理机制"),
    ("BV1kpbv6LEsm", "每天练枪还是没提升 你可能一直在犯这12个错误"),
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
