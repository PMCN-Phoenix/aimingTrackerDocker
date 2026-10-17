# -*- coding: utf-8 -*-
"""抓取精选B站视频字幕：远距离目标连续击打与贴近反应（Q004.6）"""
import sys, json, time, hashlib, urllib.parse, requests, re, os
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

def get_cid(bvid):
    r = s.get(f"https://www.bilibili.com/video/{bvid}/", timeout=20)
    m = re.search(r'window\.__INITIAL_STATE__=(.*?);\(function', r.text, re.S)
    if not m:
        m = re.search(r'window\.__INITIAL_STATE__=(.*?);\s*</script>', r.text, re.S)
    d = json.loads(m.group(1))
    v = d['videoData']
    return v['aid'], v['cid'], v['title']

def get_subtitle(bvid, cid):
    cookie = pool.get_cookie()
    s.headers["Cookie"] = cookie
    nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=15).json()
    wbi = nav["data"]["wbi_img"]
    img = wbi["img_url"].rsplit("/",1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/",1)[-1].split(".")[0]
    mixin_key = "".join((img+sub)[i] for i in MIXIN)[:32]
    p = {'bvid': bvid, 'cid': cid, 'wts': str(int(time.time()))}
    q = urllib.parse.urlencode(sorted(p.items()))
    p['w_rid'] = hashlib.md5((q+mixin_key).encode()).hexdigest()
    r = s.get("https://api.bilibili.com/x/player/wbi/v2", params=p, timeout=20)
    subs = r.json()['data']['subtitle']['subtitles']
    if not subs:
        return None
    sub_url = subs[0]['subtitle_url']
    if sub_url.startswith('//'):
        sub_url = 'https:' + sub_url
    r2 = s.get(sub_url, timeout=20)
    return r2.json()

targets = [
    ("BV1nT411K7Lr", "转火最佳Kovaak场景（中字）"),
    ("BV117421f7qM", "微调指南-让瞄准更一致（中字）"),
    ("BV1fFnAzkEZn", "xen2-甩枪轻松提升十倍的简单技巧（中字）"),
    ("BV1G24y1q79o", "TenZ-甩枪秘诀（训练场自述）"),
    ("BV1bfoTBLEP8", "2026转火初阶系统教学7500字"),
    ("BV1F64y1r79y", "世界第一定位教你定位瞄准（中字）"),
    ("BV1dreSzTE8v", "xen2-转火如何在FPS高效连杀（中字）"),
    ("BV1nSVt6SENx", "VT Multiclick 120求助帖"),
    ("BV1mU18YDEP9", "克礼无明-远距离定位拉过头直播问答"),
    ("BV19h4y197zQ", "100T职业哥修正瞄准3Tips"),
    ("BV1GhXNYkEhh", "电坤小子-顿悟微调核心"),
    ("BV19XvXB8EfX", "xen2-甩枪正在摧毁你的进步（中字）"),
    ("BV15ZqYBVEEy", "MattyOW-Evasive转火怎么练（熟肉）"),
    ("BV1u7RKBqEYL", "monkey猴-暴力甩枪与稳定定位"),
]

out_dir = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q004-场景技术问题\子问题\Q004.6-Multiclick远距离目标连续击打与贴近反应\B站原始数据\字幕"
os.makedirs(out_dir, exist_ok=True)

ok, fail = 0, 0
for bvid, desc in targets:
    print(f"\n=== {bvid} {desc} ===")
    try:
        aid, cid, title = get_cid(bvid)
        print(f"  标题: {title}")
        sub = get_subtitle(bvid, cid)
        if sub and 'body' in sub:
            texts = [x['content'] for x in sub['body']]
            full_text = '\n'.join(texts)
            safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)[:50]
            filepath = os.path.join(out_dir, f"{bvid}_{safe_title}.txt")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n# bvid: {bvid}\n# 字数: {len(full_text)}\n\n")
                f.write(full_text)
            print(f"  OK 字幕已保存 ({len(sub['body'])}段, {len(full_text)}字)")
            ok += 1
            pool.report_success()
        else:
            print("  !! 无AI字幕")
            fail += 1
    except Exception as e:
        print(f"  XX 错误: {e}")
        fail += 1
    time.sleep(2)

print(f"\n=== 完成：成功 {ok}，无字幕/失败 {fail} ===")
