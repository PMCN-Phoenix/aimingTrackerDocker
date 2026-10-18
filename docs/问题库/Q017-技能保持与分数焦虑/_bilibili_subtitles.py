# -*- coding: utf-8 -*-
"""抓取精选B站视频字幕（Q017 技能保持与分数焦虑）"""
import sys, json, os, re, time, requests
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

OUT = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q017-技能保持与分数焦虑\B站原始数据\字幕"
os.makedirs(OUT, exist_ok=True)

PICKED = [
    "BV1ENHX6KELw",  # Aimlabs数据完整解读｜别再只看最高分！告别练枪分数焦虑
    "BV1mE421A7pH",  # yRinth 流畅瞄准：通过比其他人慢来占主导
    "BV12b8L6YEJA",  # 你不是状态差，而是瞄准太僵硬｜全FPS科学控鼠和跟枪进阶理论
    "BV1kpbv6LEsm",  # 每天练枪还是没提升？你可能一直在犯这12个错误
    "BV1AQKr63EQZ",  # KovaaK's 1300小时无瓶颈之人浅谈瞄准训练
    "BV1wbT2zvEFy",  # 前职业选手教你如何科学的保持状态稳定性消除打瓦焦虑
    "BV1q7tX6UEH4",  # Garoouu 练枪很久没效果，分数实战不转化
    "BV1BRtT6dERx",  # Aimforge（七）训练平台期
    "BV14XoZBHEoq",  # TED 怎么避免压力下发挥失常
    "BV1tHp16NESU",  # VEI_J 多巴胺陷阱 毁掉排位手感
    "BV1fbjo6qE7L",  # Viscose 你瞄准训练所犯的每一个错误
    "BV1iD67BCEP5",  # 焚诀 洲瓦前职业练枪分享
    "BV1dY411P7j7",  # 三天苦练网格射击 分数直升9w
]

def get_cookie():
    return pool.get_cookie()

def safe_name(t):
    return re.sub(r'[\\/:*?"<>|\n\r]', "_", t)[:80]

def fetch(bvid):
    s.headers["Cookie"] = get_cookie()
    info = s.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", timeout=20).json()
    if info.get("code") != 0:
        return bvid, None, f"view code={info.get('code')}"
    title = re.sub(r"<[^>]+>", "", info["data"]["title"])
    cid = info["data"]["cid"]
    player = s.get("https://api.bilibili.com/x/player/wbi/v2", params={"bvid": bvid, "cid": cid}, timeout=20)
    pdata = player.json()
    subs = pdata.get("data", {}).get("subtitle", {}).get("subtitles", [])
    if not subs:
        return bvid, (title, None), "无字幕"
    url = ("https:" + subs[0]["subtitle_url"]) if subs[0]["subtitle_url"].startswith("//") else subs[0]["subtitle_url"]
    body = s.get(url, timeout=25).json()
    lines = [seg["content"] for seg in body.get("body", [])]
    return bvid, (title, "\n".join(lines)), f"{len(lines)}行"

ok, miss = 0, 0
for bvid in PICKED:
    try:
        bvid, data, msg = fetch(bvid)
        if data and data[1]:
            title, text = data
            with open(os.path.join(OUT, f"{bvid}_{safe_name(title)}.txt"), "w", encoding="utf-8") as f:
                f.write(f"# {title}\n# {bvid}\n\n{text}")
            print(f"  ✅ {bvid} {title[:40]} ({msg})")
            ok += 1
        else:
            print(f"  ❌ {bvid} {msg}")
            miss += 1
    except Exception as e:
        print(f"  ❌ {bvid} 错误: {e}")
        miss += 1
    time.sleep(2)

print(f"\n字幕完成: {ok} 成功 / {miss} 失败")
