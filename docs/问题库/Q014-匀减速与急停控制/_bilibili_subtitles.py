# -*- coding: utf-8 -*-
"""抓取精选B站视频字幕：匀减速 vs 制动式急停（Q014）"""
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
    ("BV1eRm8YeEJx", "甜糖-瞄准的减速过程有哪些方法（正中靶心）"),
    ("BV1AA41157w8", "大东彦-自瞄般机械锁住的感觉"),
    ("BV1L23z6eEYg", "钚荟画-平滑瞄准发力进阶四千小时"),
    ("BV1bK411a7au", "琪露诺-4000h平滑跟枪理解"),
    ("BV1dEeUzPEGk", "xen2-跟枪瞄准训练方法（中字）"),
    ("BV17k4y1S7HW", "MattyOW-Scucchi平滑上帝Ep4（中字）"),
    ("BV1mE421A7pH", "流畅瞄准-通过比其他人慢占主导（中字）"),
    ("BV16eaA6bE9F", "晨曜-卸力与制动禁忌火车模型（Q007核心）"),
    ("BV1C2Hi6AEAa", "晨曜-微调一快就空观察发力训练"),
    ("BV1aXyuYeEc8", "姚大韬-手指才是微调关键（反面意见）"),
    ("BV1zf546mEfn", "CKY811-世界上最好的跟枪图"),
    ("BV1ob421n7E3", "画木啄眉-Smoothness Trainer Robot"),
    ("BV18sJb67Eqf", "Lew-训练最平滑的瞄准（中配）"),
    ("BV11T4y1i7eb", "Aimbeast Smooth V2 平滑跟枪入门"),
]

out_dir = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q014-匀减速与急停控制\B站原始数据\字幕"
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
