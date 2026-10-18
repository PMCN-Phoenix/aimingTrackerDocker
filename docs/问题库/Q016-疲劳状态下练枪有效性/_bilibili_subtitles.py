# -*- coding: utf-8 -*-
"""B站字幕抓取：Q016 疲劳状态下练枪有效性"""
import sys, json, time, requests, re, os
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

SELECTED = [
    ("BV1ojmVYxEv1", "纵欲过度会影响瞄准？游戏水平会因为熬夜而降低吗"),
    ("BV1dz421y72z", "为什么越打状态越差？为什么练枪转化低？影响瞄准水平的游戏外部因素"),
    ("BV1PA411U7YK", "熬夜打游戏反应力随时间持续下降吗？我做了实验"),
    ("BV13XYT6dEGG", "别疲劳练枪 状态差练了白搭"),
    ("BV1fe4y147Gv", "打工人半夜练枪抗疲劳"),
    ("BV1GR4y1w7Jg", "运动表现下降？精神疲劳？OTS过度训练症状"),
    ("BV1vs4y137cP", "如何辨别自己疲劳又如何尽快恢复 国家队教练"),
    ("BV1kpbv6LEsm", "每天练枪还是没提升 12个错误 Aimlabs"),
    ("BV1i19RBUEzV", "别再无效练枪了 英杰教练"),
    ("BV1qt421a7Zu", "为什么说你的练枪是自我感动的偷懒"),
    ("BV1gZwKzREnZ", "你可怕的疲劳③ 神经疲劳"),
    ("BV14M4m197t2", "脑力工作者的3种累与3种休息方式"),
    ("BV13Pep6BEGt", "这是认知疲劳 感官过载"),
    ("BV12b8L6YEJA", "你不是状态差而是瞄准太僵硬"),
    ("BV1fbjo6qE7L", "Viscose 你瞄准训练所犯的每一个错误"),
    ("BV1YkmFB6EGQ", "训练经常神经疲劳到底应该怎么办"),
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
