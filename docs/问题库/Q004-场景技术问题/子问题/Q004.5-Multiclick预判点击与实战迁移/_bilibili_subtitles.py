# -*- coding: utf-8 -*-
"""B站字幕抓取：Q004.5 Multiclick预判点击与实战迁移（精选12个）"""
import sys, json, time, re, os, requests
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

OUT = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q004-场景技术问题\子问题\Q004.5-Multiclick预判点击与实战迁移\B站原始数据\字幕"
os.makedirs(OUT, exist_ok=True)

SELECTED = [
    ("BV1tq4y1A7yA", "5分钟化身预瞄之神，全网最实用的预瞄教学"),
    ("BV1Q6PmeREP6", "FPS游戏最容易陷入的瞄准误区！先瞄准再开枪与冷静瞄准"),
    ("BV1mtSRBxEk6", "最通俗易懂的走路、预瞄、准星摆放教学"),
    ("BV1FLmjBPExk", "29岁反应慢定位差，我是怎么靠预瞄打上赋能的"),
    ("BV1ef42197Uv", "看到人了反应不过来是为什么"),
    ("BV1Q18Fz2E2e", "因为预瞄太烂 所以用反应解决了一切"),
    ("BV1mAPRePE3b", "你的分段预瞄为什么不干净且没有效果"),
    ("BV1zZoQB9EAB", "极致预瞄 纯净瞄准 干爽走路 大基本功身位控制"),
    ("BV1DU411U7kV", "学院派预瞄是怎么打瓦的"),
    ("BV1hk4y197N1", "新手教学 你真的学会预瞄了吗"),
    ("BV1hEA5z7EMd", "无畏契约全段位通用的实用预瞄技巧"),
    ("BV1Zb4y1L75N", "最全面的预瞄教学 全地图预瞄流程演示上"),
]

def cookie():
    s.headers["Cookie"] = pool.get_cookie()

def get_view(bvid):
    cookie()
    r = s.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", timeout=20).json()
    if r.get("code") != 0:
        return None
    return r["data"]

def get_player_info(bvid, cid):
    cookie()
    r = s.get(f"https://api.bilibili.com/x/player/wbi/v2?bvid={bvid}&cid={cid}", timeout=20).json()
    if r.get("code") != 0:
        return None
    return r["data"].get("subtitle", {})

def clean(text):
    text = re.sub(r"\s+", " ", text).strip()
    return text

ok, miss = 0, 0
for bvid, name in SELECTED:
    out_path = os.path.join(OUT, f"{bvid}_{name[:40]}.txt")
    if os.path.exists(out_path):
        print(f"跳过（已存在）: {name}")
        continue
    try:
        v = get_view(bvid)
        if not v:
            print(f"[x] view失败: {bvid}")
            miss += 1
            continue
        cid = v["cid"]
        sub = get_player_info(bvid, cid)
        subs = (sub or {}).get("subtitles", [])
        if not subs:
            print(f"[无AI字幕] {name} | 播放={v['stat']['view']}")
            miss += 1
            time.sleep(1.2)
            continue
        sub_url = ("https:" if subs[0]["subtitle_url"].startswith("//") else "") + subs[0]["subtitle_url"]
        cookie()
        body = s.get(sub_url, timeout=20).json()
        lines = []
        for item in body.get("body", []):
            t = item.get("from", 0)
            mm, sec = int(t // 60), t % 60
            lines.append(f"[{mm:02d}:{sec:05.2f}] {clean(item.get('content',''))}")
        text = "\n".join(lines)
        if len(text) < 80:
            print(f"[字幕过短] {name} | {len(text)}字符")
            miss += 1
            continue
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"来源: https://www.bilibili.com/video/{bvid}\n标题: {name}\n作者: {v['owner']['name']} 播放: {v['stat']['view']}\n时长: {v['duration']}s 字幕行数: {len(lines)}\n\n" + text)
        print(f"[OK] {name} | {len(lines)}行 | 播放={v['stat']['view']}")
        ok += 1
        time.sleep(1.8)
    except Exception as e:
        print(f"[错误] {name}: {e}")
        miss += 1
        time.sleep(1.5)

print(f"\n完成: {ok} 成功, {miss} 失败/无字幕")
