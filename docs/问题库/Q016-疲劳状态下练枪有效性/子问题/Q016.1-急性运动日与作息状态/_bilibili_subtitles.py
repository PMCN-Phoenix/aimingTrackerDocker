# -*- coding: utf-8 -*-
"""抓取精选B站视频字幕：作息/运动/睡眠/状态对瞄准影响（Q016）"""
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
    ("BV1LQEsz8EGM", "后湖婆婆-跑步提升游戏反应与专注（3个月实验）"),
    ("BV1cvng6QEo3", "Aimforge-全网最科学FPS分析之睡眠"),
    ("BV1r5gPzRE3U", "瓦洛兰特-当我拥有充足的睡眠"),
    ("BV12b8L6YEJA", "边学边主播-你不是状态差而是瞄准太僵硬（科学控鼠）"),
    ("BV1ecbAznETh", "艾锐克斯-如何解决瞄准时手抖（KOVAAK熟肉）"),
    ("BV1WR4y1p75a", "吃个面包吧-改善练枪手抖"),
    ("BV1uUKp6hEEq", "糯玉米真好吃Val-一瞄准就手抖是控鼠发力错了"),
    ("BV1M3411C7Ld", "三零VAL-nAts每日热身迅速进入竞技状态"),
    ("BV1q3LP6LELk", "哭哭瓦-四项热身练习迅速进入状态"),
    ("BV19N556KE9E", "大雄Elijah-顶级运动员视角下的睡眠科学"),
    ("BV1UM411p7a6", "职业哥1V3也紧张到手抖"),
    ("BV1cNAkeHECf", "认真的小宇哥-30+如何保持最佳电竞状态"),
    ("BV1hfGB68ESJ", "Ryanguru-FPS职业教练瞄准讲座基础"),
    ("BV1vSQYBUEEb", "鱼博士-熬夜的定义和危害"),
    ("BV1R4411m7Wg", "TED-睡觉才是王道睡眠是超能力"),
]

out_dir = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q016-日常作息运动与瞄准状态\B站原始数据\字幕"
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
