# -*- coding: utf-8 -*-
"""抓取精选新视频字幕：web HTML 拿 aid/cid -> wbi /x/player/wbi/v2 -> 下载字幕 json + txt"""
import requests, re, json, time, hashlib, urllib.parse, os, sys

sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

OUT_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景\18-拉出去打不到人-B站原始数据"
SUB_DIR = os.path.join(OUT_DIR, '字幕')
os.makedirs(SUB_DIR, exist_ok=True)

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'})
s.headers['Cookie'] = pool.get_cookie()

nav = s.get('https://api.bilibili.com/x/web-interface/nav', timeout=20).json()
wbi = nav['data']['wbi_img']
img = wbi['img_url'].rsplit('/', 1)[-1].split('.')[0]
sub = wbi['sub_url'].rsplit('/', 1)[-1].split('.')[0]
MIXIN_KEY = ''.join((img + sub)[i] for i in MIXIN)[:32]

def sign(params):
    p = dict(params)
    p['wts'] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p['w_rid'] = hashlib.md5((q + MIXIN_KEY).encode()).hexdigest()
    return p

def get_state(bvid):
    """抓网页 HTML 拿 __INITIAL_STATE__（绕 412）"""
    r = s.get(f'https://www.bilibili.com/video/{bvid}/', timeout=25)
    t = r.text
    m = (re.search(r'window\.__INITIAL_STATE__=(.*?);\(function', t, re.S)
         or re.search(r'window\.__INITIAL_STATE__=(.*?);\s*</script>', t, re.S))
    return json.loads(m.group(1))['videoData']

def fmt_ts(sec):
    sec = int(sec)
    h = sec // 3600; m = (sec % 3600) // 60; ss = sec % 60
    return f'{h}:{m:02d}:{ss:02d}' if h else f'{m}:{ss:02d}'

TARGETS = [
    ('BV12DevesEtF', '《又学到了！》大拉就是拉出去对枪吗？到底怎么出掩体才不会被秒呢？', '斯米马赛z'),
    ('BV16exyeUEEy', '【登神瓦课】#4 为什么你拉出去就被秒？该如何正确的peek？', '好家伙不演了'),
    ('BV14SkuYSELX', '黄金和下三段玩家最常出现的对枪问题-瞄准和移动的关系-无畏契约小贴士#5', '暗辰の薄明'),
    ('BV1tq4y1A7yA', '5分钟化身预瞄之神，全网最实用的预瞄教学！全FPS通用！', '大东彦'),
    ('BV1eehiz9EEc', '目标一动就马枪？一个视频让你真正学会动态定位！【瓦瞄准修炼秘籍4】', '晨曜cheyo'),
    ('BV1Q6PmeREP6', 'FPS游戏最容易陷入的瞄准误区！先瞄"准"再开枪与"冷静"瞄准', '电坤小子嘿嘿'),
]

results = []
for bvid, title, author in TARGETS:
    rec = {'bvid': bvid, 'title': title, 'author': author, 'status': ''}
    try:
        vd = get_state(bvid)
        aid = vd['aid']; cid = vd['cid']; dur = vd.get('duration', 0)
        rec['aid'] = aid; rec['cid'] = cid; rec['duration'] = dur
        # wbi 字幕接口
        subs = []
        for attempt in range(4):
            q = sign({'bvid': bvid, 'cid': str(cid), 'web_location': '333.1007'})
            d = s.get('https://api.bilibili.com/x/player/wbi/v2', params=q,
                      headers={'Referer': f'https://www.bilibili.com/video/{bvid}/'}, timeout=20).json()
            sublist = ((d.get('data') or {}).get('subtitle') or {}).get('subtitles') or []
            if sublist:
                subs = sublist
                break
            time.sleep(3)
        if not subs:
            rec['status'] = '无AI字幕'
            print(f'{bvid} 无AI字幕，跳过')
            results.append(rec)
            continue
        pick = next((x for pref in ['zh-Hans', 'zh-CN', 'zh', 'ai-zh'] for x in subs if x.get('lan') == pref), subs[0])
        u = pick['subtitle_url']
        if u.startswith('//'):
            u = 'https:' + u
        body = s.get(u, headers={'Referer': f'https://www.bilibili.com/video/{bvid}/'}, timeout=25).json()['body']
        # 落 json
        with open(os.path.join(SUB_DIR, f'{bvid}.json'), 'w', encoding='utf-8') as f:
            json.dump({'bvid': bvid, 'title': title, 'author': author, 'aid': aid, 'cid': cid,
                       'duration': dur, 'lan': pick.get('lan'), 'body': body}, f, ensure_ascii=False, indent=2)
        # 落 txt（带时间戳）
        lines = [f'[{fmt_ts(x["from"])}] {x["content"]}' for x in body]
        with open(os.path.join(SUB_DIR, f'{bvid}.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        cov = body[-1]['to'] / dur if dur else 0
        rec['status'] = f'OK({len(body)}段, 覆盖{cov:.0%})'
        print(f'{bvid} OK | {len(body)}段 | 覆盖{cov:.0%} | {title[:30]}')
    except Exception as e:
        rec['status'] = f'FAIL: {e}'
        print(f'{bvid} FAIL: {e}')
    results.append(rec)
    time.sleep(2)

with open(os.path.join(OUT_DIR, '抓取状态.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('\n完成')
