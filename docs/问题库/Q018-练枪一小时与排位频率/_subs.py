# -*- coding: utf-8 -*-
"""抓取「排位频率 / 练枪时长 / 生活平衡 / 持续进步」主题字幕。"""
import sys, time, requests, re, os
sys.path.insert(0, r"D:/11.project/iwen-codex/bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

SELECTED = [
    ("BV1K94y1E7Z8", "每天练枪一小时 这是她瞄准发生的变化"),
    ("BV1qoAceeEpf", "花太多时间在瞄准训练上的样子"),
    ("BV1JWtEe7EvX", "400小时卡黄金 每天练枪一打排位就软"),
    ("BV1m14y1q7rX", "练枪软件与实战转化效率"),
    ("BV1aupu6qEuD", "神话杂谈 上分练枪经验分享"),
    ("BV1ga37zyETR", "300小时上超凡 我是如何练枪的"),
    ("BV11m41117E5", "训练计划 无畏契约 全段位合集"),
    ("BV1AQKr63EQZ", "KovaaK 1300小时无瓶颈谈瞄准训练"),
    ("BV1RC4y1m744", "woohoojin 不敢打排位"),
    ("BV1kpbv6LEsm", "每天练枪还是没提升 12个错误"),
    ("BV1pA3Sz9EzL", "FPS科学提升技术 快速提升计划"),
    ("BV1F4bv6CErJ", "排位加分少掉分多 加分机制"),
    ("BV1dXpf6nEMC", "1000小时kovaak经验总结"),
    ("BV1s9HgzkE9L", "不练枪只排位真上不了分"),
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
