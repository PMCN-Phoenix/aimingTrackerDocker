# -*- coding: utf-8 -*-
"""抓取精选B站视频字幕：周边视觉/注意力分配（Q015）"""
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
    ("BV1rP5ezUEfC", "康康-注意力在准星用余光看人（职业哥自述）"),
    ("BV1Mo5jzJEU1", "nblfps-为什么注意力要在准星用余光看人"),
    ("BV1Fay8YzEyu", "KiddoJioJio-注意力分配教学"),
    ("BV17pMg6mEy8", "虞姬电竞-高级FPS眼部追踪（147万播放）"),
    ("BV1Wnthz7Eh9", "VEI_J-反应速度怎么变快（中字）"),
    ("BV1PHhB6hEqh", "VEI_J-进阶FPS视觉训练提升跟枪与反应（中字）"),
    ("BV1aUZZYBEBY", "VEI_J-怎么更快培养游戏意识（中字）"),
    ("BV1Q6421f7aX", "吃个面包吧-眼部训练热身（137万播放）"),
    ("BV1BA4y1D7GY", "大东彦-反应速度不只是天赋"),
    ("BV1RWLHzgErQ", "疾风扳机015-前职业选手科学提高反应速度"),
    ("BV17y9eBfEpZ", "咕咕药丸-顶尖FPS高手的底层逻辑"),
    ("BV11XqGY1E9n", "大东彦-极致预瞄预预症"),
    ("BV1KBJy69Ess", "Ethan-宝宝式预瞄训练"),
    ("BV1LQEsz8EGM", "后湖婆婆-跑步提升游戏反应与专注"),
    ("BV1Hr4y1W7so", "翠鸟视觉-视野科普余光原理"),
]

out_dir = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q015-周边视觉与注意力分配\B站原始数据\字幕"
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
