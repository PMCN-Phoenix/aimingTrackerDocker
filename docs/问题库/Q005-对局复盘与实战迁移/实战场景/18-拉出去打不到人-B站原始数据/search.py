# -*- coding: utf-8 -*-
"""B站搜索：拉出去打不到人（peek/swing 瞄准落空）
3主题 x 3组关键词 = 9组，wbi签名，Cookie池轮询。
"""
import requests, re, json, time, hashlib, urllib.parse, os, sys

sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

OUT_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景\18-拉出去打不到人-B站原始数据"
os.makedirs(OUT_DIR, exist_ok=True)

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'})
s.headers['Cookie'] = pool.get_cookie()

# nav 拿 wbi key
nav = s.get('https://api.bilibili.com/x/web-interface/nav', timeout=20).json()
print('nav isLogin:', (nav.get('data') or {}).get('isLogin'))
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

def search_one(kw, page):
    p = sign({'search_type': 'video', 'keyword': kw, 'page': page, 'page_size': 30})
    r = s.get('https://api.bilibili.com/x/web-interface/wbi/search/type', params=p, timeout=25)
    if r.status_code == 412 or '"code":-412' in r.text:
        pool.report_412()
        s.headers['Cookie'] = pool.get_cookie()
        print(f'  412! 换号重试...')
        time.sleep(3)
        r = s.get('https://api.bilibili.com/x/web-interface/wbi/search/type', params=sign({'search_type': 'video', 'keyword': kw, 'page': page, 'page_size': 30}), timeout=25)
    else:
        pool.report_success()
    d = r.json()
    if d.get('code') != 0:
        print(f'  ERR {kw} p{page}: {d.get("code")} {d.get("message")}')
        return []
    res = (d.get('data') or {}).get('result') or []
    out = []
    for v in res:
        if v.get('type') != 'video':
            continue
        title = re.sub(r'<[^>]+>', '', v.get('title', ''))
        out.append({
            'bvid': v.get('bvid', ''),
            'title': title,
            'author': v.get('author', ''),
            'play': v.get('play', 0),
            'duration': v.get('duration', ''),
            'pubdate': v.get('pubdate', 0),
            'desc': (v.get('description') or '')[:200],
            'kw': kw,
        })
    return out

KEYWORDS = [
    # 主题A 拉枪/拉出打不到
    '拉出去打不到人',
    '拉枪打不到人',
    '大拉打不到人',
    # 主题B 预瞄与peek
    '预瞄 头线',
    '拉出掩体 预瞄',
    'peek 教学 打不到',
    # 主题C 急停与甩枪
    '急停 打不准',
    '甩枪 过头',
    '移动中开枪 不准',
]

all_videos = {}
kw_stats = {}
for kw in KEYWORDS:
    n = 0
    for page in [1, 2]:
        try:
            results = search_one(kw, page)
            for v in results:
                bv = v['bvid']
                if bv and bv not in all_videos:
                    all_videos[bv] = v
                    n += 1
            time.sleep(1.5)
        except Exception as e:
            print(f'  EXC {kw} p{page}: {e}')
    kw_stats[kw] = n
    print(f'搜索: {kw} | 新增 {n} | 累计去重 {len(all_videos)}')

print('\n=== 关键词统计（新增数）===')
for k, v in kw_stats.items():
    print(f'  {k}: {v}')
print(f'总去重: {len(all_videos)}')

# ---- 打分 ----
def dur_to_sec(d):
    if not d: return 0
    parts = str(d).split(':')
    try:
        if len(parts) == 2: return int(parts[0]) * 60 + int(parts[1])
        if len(parts) == 3: return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except Exception:
        return 0
    return 0

W = [
    # 核心症状词
    ('打不到', 10), ('打不准', 10), ('瞄不到', 8), ('马枪', 6), ('马', 0),
    # 动作词
    ('拉出去', 8), ('拉出', 6), ('大拉', 7), ('拉枪', 7), ('peek', 8), ('swing', 6),
    ('急停', 8), ('甩枪', 8), ('甩', 2), ('预瞄', 8), ('头线', 8), ('爆头线', 8),
    ('架枪', 5), ('掩体', 5), ('身位', 5), ('定位', 5), ('瞄准', 4),
    # 游戏限定（非游戏内容降权）
    ('无畏契约', 4), ('valorant', 4), ('瓦罗兰特', 4), ('瓦', 1), ('csgo', -6), ('cs2', -6),
    ('apex', -6), ('吃鸡', -6), ('和平精英', -8), ('cf', -4),
]

def score(v):
    t = (v['title'] + ' ' + v.get('desc', '')).lower()
    s = sum(w for k, w in W if k.lower() in t)
    p = v.get('play') or 0
    s += 4 if p > 100000 else 3 if p > 30000 else 2 if p > 5000 else 0
    dur = dur_to_sec(v.get('duration', ''))
    if dur < 45: s -= 4
    if dur > 900: s += 0  # 长视频不额外加分
    return s

scored = sorted(all_videos.values(), key=lambda x: score(x), reverse=True)
for v in scored:
    v['_score'] = score(v)
    v['_dur_sec'] = dur_to_sec(v.get('duration', ''))

with open(os.path.join(OUT_DIR, '搜索清单-全量.json'), 'w', encoding='utf-8') as f:
    json.dump({'kw_stats': kw_stats, 'total_dedup': len(scored), 'videos': scored}, f, ensure_ascii=False, indent=2)

print('\n=== Top 40 ===')
for i, v in enumerate(scored[:40]):
    print(f"{i+1:2d}. [{v['_score']:3d}] {v['bvid']} | play={v['play']:>7} | {v['duration']:>7} | {v['title'][:38]} | {v['author']}")
