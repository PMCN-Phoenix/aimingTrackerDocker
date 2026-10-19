# -*- coding: utf-8 -*-
"""B站字幕抓取：Q021 转火过头与跟踪切换损耗"""
import sys, json, time, requests, re, os
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

SELECTED = [
    ("BV1AsJ16pEod", "瓦近距离总微调过头 别再只刷六目标"),
    ("BV1sZtf61EFL", "AA4V跟枪大神的终极焚决 欠瞄"),
    ("BV1XB421B792", "如何做到外挂一样的转火"),
    ("BV1wT4y117ys", "COD战地玩家必看 转火篇"),
    ("BV1bs4y1w7HG", "保姆级教学教你顶尖转火"),
    ("BV1C2Hi6AEAa", "微调一快就空一慢就被秒 观察发力训练"),
    ("BV1aXyuYeEc8", "手指才是微调的关键"),
    ("BV13jNs6TE6u", "臂腕切换 全方位无死角精确瞄准"),
    ("BV1dzuBzkE8m", "如何实现最稳定的甩枪操作"),
    ("BV1fuWAzjEei", "一次定位很差但是微调无敌"),
    ("BV1nT411K7Lr", "练习转火的最佳Kovaak场景"),
    ("BV1faTd6VEEG", "日本转火高手nanami的转火tips"),
    ("BV1kFJb6eELs", "中文互联网最好的瞄准发力教学"),
    ("BV1mV411H77V", "细说眼睛对瞄准的影响"),
    ("BV1eZ4y147M4", "不同瞄准策略在1w9000ts上的差异"),
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
