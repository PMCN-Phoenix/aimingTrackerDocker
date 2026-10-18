# -*- coding: utf-8 -*-
"""抓取「抖动 / 控鼠发力 / 手腕 / 张力控制 / 微调」主题字幕。"""
import sys, time, requests, re, os
sys.path.insert(0, r"D:/11.project/iwen-codex/bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

SELECTED = [
    ("BV1uUKp6hEEq", "一瞄准就手抖 控鼠发力错了"),
    ("BV1YM4y1M7Ro", "你真的会选择合适的鼠标握法吗 手腕流手臂流谎言"),
    ("BV1A9KpzTEHL", "张力控制全攻略"),
    ("BV1RC411E7Ck", "准星乱抖 瞄头吃力"),
    ("BV1kFJb6eELs", "中文互联网最好的瞄准发力教学"),
    ("BV1318t63Ewc", "弹道飘准星抖 先检查这三项"),
    ("BV1Jg411i7CR", "5分钟快速提升微调能力"),
    ("BV1GhXNYkEhh", "顿悟微调核心"),
    ("BV1654y1d73x", "APEX跟枪不是无数次的定位"),
    ("BV1VEp7zCE7j", "五阶灵敏度"),
]


def get_cid(b):
    r = s.get(f"https://api.bilibili.com/x/web-interface/view?bvid={b}", timeout=20).json()
    return (r["data"]["cid"], None) if r.get("code") == 0 else (None, r.get("message"))


def sub_url(b, c):
    r = s.get(f"https://api.bilibili.com/x/player/wbi/v2?bvid={b}&cid={c}", timeout=20).json()
    subs = r.get("data", {}).get("subtitle", {}).get("subtitles", [])
    if not subs:
        return None
    subs.sort(key=lambda x: 0 if "zh" in x.get("lan", "") else 1)
    return subs[0].get("subtitle_url", "")


out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "B站原始数据", "字幕")
os.makedirs(out, exist_ok=True)
ok = 0
for b, t in SELECTED:
    safe = re.sub(r'[\\/:*?"<>|]', "_", t)[:50]
    p = os.path.join(out, f"{b}_{safe}.txt")
    if os.path.exists(p):
        ok += 1
        continue
    try:
        s.headers["Cookie"] = pool.get_cookie()
        cid, err = get_cid(b)
        if not cid:
            print(f"  cid失败 {b} {err}")
            continue
        u = sub_url(b, cid)
        if not u:
            print(f"  无字幕 {b} {t[:24]}")
            continue
        if u.startswith("//"):
            u = "https:" + u
        j = s.get(u, timeout=20).json()
        txt = "\n".join(i["content"] for i in j.get("body", []))
        open(p, "w", encoding="utf-8").write(f"# {t}\n# {b}\n\n" + txt)
        ok += 1
        print(f"  OK {b} ({len(txt)}字) {t[:24]}")
    except Exception as e:
        print(f"  ERR {b} {e}")
    time.sleep(1.5)
print(f"完成 {ok}/{len(SELECTED)}")
