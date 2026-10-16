# -*- coding: utf-8 -*-
"""抓取精选B站视频字幕：Reflex Flick - Easy 定位慢/甩不过去（Q004.4）"""
import sys, json, time, hashlib, urllib.parse, requests, re, os
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

def get_cid(bvid):
    """从网页HTML拿aid和cid"""
    r = s.get(f"https://www.bilibili.com/video/{bvid}/", timeout=20)
    m = re.search(r'window\.__INITIAL_STATE__=(.*?);\(function', r.text, re.S)
    if not m:
        m = re.search(r'window\.__INITIAL_STATE__=(.*?);\s*</script>', r.text, re.S)
    d = json.loads(m.group(1))
    v = d['videoData']
    return v['aid'], v['cid'], v['title']

def get_subtitle(bvid, cid):
    """用wbi签名拿AI字幕"""
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

# 精选视频（按相关度排序）
targets = [
    ("BV1hQ9rBTECC", "Reflex Flick Easy 6500 无法突破之人（正中靶心：同场景卡分）"),
    ("BV1We4y1X75D", "[中字]静态点击教程 - 常见的错误和缺陷"),
    ("BV15Z421K779", "【MattyOW】流畅性：静态点击的关键 - 揭开瞄准的秘密 Ep.6"),
    ("BV1F64y1r79y", "[中字][Kovaak练枪指南] 世界第一定位教你定位瞄准"),
    ("BV14w411B7t2", "【FPS干货】练枪3400小时后分享对静态定位的进阶理解"),
    ("BV1T3he6QEwd", "只需3个练习 掌握定位 微调的确认感"),
    ("BV1CX396dEoE", "一分钟视频教会你 如何学会甩枪"),
    ("BV14y4y187bn", "世界第一定位的kovaak静态瞄准指南"),
    ("BV1Rt4y1s7dt", "近期KovaaKs大师静态定位练枪合集"),
    ("BV1mE421A7pH", "[中字]流畅瞄准：通过比其他人慢来占主导地位的奇怪方式"),
    ("BV1HoYWzMEXv", "【瞄准急救】Flick(甩）正义の 流体美学"),
    ("BV1sW42197gU", "定位、微调差，怎么办"),
    ("BV1C2Hi6AEAa", "微调一快就空，一慢就被秒？观察、发力、训练一次讲清"),
    ("BV1LCpwz3EXs", "【Kovaak】Valorant Reflex Flick Strafing 76分 暂居#1"),
    ("BV1hZ4y117J5", "【Kovaak 静态点击】1wall6targets small - 1202"),
]

out_dir = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q004-场景技术问题\子问题\Q004.4-ReflexFlick定位甩不过去\B站原始数据\字幕"
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
            print(f"  ✅ 字幕已保存 ({len(sub['body'])}段, {len(full_text)}字)")
            ok += 1
            pool.report_success()
        else:
            print(f"  ⚠️ 无AI字幕")
            fail += 1
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        fail += 1
    time.sleep(2)

print(f"\n=== 完成：成功 {ok}，无字幕/失败 {fail} ===")
