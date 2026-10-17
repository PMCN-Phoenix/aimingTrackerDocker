# -*- coding: utf-8 -*-
"""B站字幕抓取：Q004.7 Pokeball Frenzy 大甩与微调过度临界点"""
import sys, json, time, requests, re, os
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

# 精选清单: (bvid, 标题)
SELECTED = [
    ("BV1C2Hi6AEAa", "微调一快就空，一慢就被秒？观察、发力、训练一次讲清"),
    ("BV1m38E6kEsA", "【Viscose测试】Pokeball Frenzy Auto TE Wide 4260 silk"),
    ("BV1We4y1X75D", "[中字]静态点击教程 - 常见的错误和缺陷"),
    ("BV1AZ4y1w7EW", "[熟肉]如何甩的更准？手腕甩枪的奥秘！"),
    ("BV15Z421K779", "【MattyOW】流畅性：静态点击的关键"),
    ("BV14w411B7t2", "【FPS干货】练枪3400小时后分享对静态定位的进阶理解"),
    ("BV19XvXB8EfX", "[中字]甩枪正在摧毁你的进步"),
    ("BV1ARP3e6EuF", "【外设讲堂】直线修正真的会影响微调吗"),
    ("BV1T3he6QEwd", "只需3个练习 掌握定位 微调的确认感"),
    ("BV1sW42197gU", "定位、微调差，怎么办"),
    ("BV1XPXYBVEzm", "FPS游戏科学控鼠发力（短TTK篇）"),
    ("BV1mE421A7pH", "[中字]流畅瞄准：通过比其他人慢来占主导地位的奇怪方式"),
    ("BV1u7RKBqEYL", "怎么拥有暴力的甩枪和稳定的定位看这期就够了"),
    ("BV1pQuN6LEwd", "手腕流还是手臂流？用一个训练找准你的有效瞄准范围"),
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
    # 优先中文字幕
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
