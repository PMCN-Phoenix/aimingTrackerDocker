# -*- coding: utf-8 -*-
"""B站字幕抓取：Q004.8 Pressure Aiming 5 Target 打法与涨分"""
import sys, json, time, requests, re, os
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

SELECTED = [
    ("BV1mY4y1e7Gh", "静态教科书 Pressure aiming 7 shortened 8400 克礼无明"),
    ("BV1ni421Y7gQ", "[中字]命中确认：每次都能完美击中目标的被低估的瞄准方法"),
    ("BV1wD5KzCE4W", "什么是瞄准确认感 7ommy"),
    ("BV1NX5gzZEnJ", "聊聊确认感与怎么提升确认感并提高瞄准能力 Ashes33"),
    ("BV1SxV56ZEGj", "1分钟让你学会瞄准确认感 spleascom"),
    ("BV16xUNY3EVx", "瓦瓦网校-确认的tips 甜糖"),
    ("BV1brJU6MEud", "绝对集中的注意力与确认感 击靶大王莉拉"),
    ("BV19Khb6SEA6", "1w6ts 1320 点击犹豫确认迟钝求解"),
    ("BV1a4t865EaR", "Aimlabs基准测试Benchmark完整指南"),
    ("BV1pe7UzKERA", "当我拥有世界上最强的确认感 MahiruOuO"),
    ("BV1Ln6ZBxE4e", "6分钟永久拯救你的瞄准 VEI_J"),
    ("BV1V6SVYoE42", "合理的瞄准窗口插入时机与极限瞄准 琪露诺"),
    ("BV1b74118715", "教你轻松提高点击鼠标速度 幕川北"),
    ("BV1hWQUBQEhB", "瞄准不稳定看这个就够了 VEI_J"),
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
