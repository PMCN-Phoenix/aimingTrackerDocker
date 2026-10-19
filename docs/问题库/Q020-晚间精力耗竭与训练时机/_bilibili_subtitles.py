# -*- coding: utf-8 -*-
"""B站字幕抓取：Q016 疲劳状态下练枪有效性"""
import sys, json, time, requests, re, os
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

SELECTED = [
    ("BV1P84y1K7j4", "工作很累下班后还能健身吗 疲劳管理量力而行"),
    ("BV13m411S7hb", "深夜分享 疲劳的时候该不该健身 睡眠不足996学生党"),
    ("BV1814y1j7Sn", "边熬夜边健身你的身体会发生哪些变化"),
    ("BV1ZL4y1G7RJ", "早晨锻炼vs晚上健身差别真的很大"),
    ("BV1Mt4y1L7Ld", "什么时间健身效果最好"),
    ("BV1CK4y1j7Lk", "每天最佳训练时间是几点"),
    ("BV19edwBAEN6", "晚上7点以后停止高强度健身 皮质醇说法待检验"),
    ("BV15E411h7UU", "如何避免健身后失眠"),
    ("BV1E14y1Z75p", "你为什么总是很累 缓解大脑疲劳的10个方法"),
    ("BV1FvXqBzE6B", "如何有效休息 从脑科学看修复疲劳"),
    ("BV1hd4y197SN", "假期性注意力涣散如何快速恢复"),
    ("BV14yJq6iEtQ", "睡前练枪 注意力分配到握鼠标的右手"),
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
