# -*- coding: utf-8 -*-
"""B站搜索：高低差对枪+穿墙+靠墙掩体 实战场景"""
import requests, re, json, time, hashlib, urllib.parse, os, sys

PY = r"D:\6_code\13_python\1_python3.11.0\python.exe"
COOKIE_FILE = r"D:\11.project\iwen-codex\bilibili-cookies\account1.txt"
OUT_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-B站原始数据"
os.makedirs(OUT_DIR, exist_ok=True)

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

def sign(params):
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    cookie = open(COOKIE_FILE, encoding='utf-8-sig').read().strip()
    s.headers['Cookie'] = cookie
    nav = s.get('https://api.bilibili.com/x/web-interface/nav', timeout=20).json()
    wbi = nav['data']['wbi_img']
    img = wbi['img_url'].rsplit('/',1)[-1].split('.')[0]
    sub = wbi['sub_url'].rsplit('/',1)[-1].split('.')[0]
    mixin = ''.join((img+sub)[i] for i in MIXIN)[:32]
    p = dict(params)
    p['wts'] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p['w_rid'] = hashlib.md5((q+mixin).encode()).hexdigest()
    return s, p

def search(kw, page=1):
    s, p = sign({'search_type': 'video', 'keyword': kw, 'page': page, 'page_size': 30})
    r = s.get('https://api.bilibili.com/x/web-interface/wbi/search/type', params=p, timeout=25)
    d = r.json()
    if d.get('code') != 0:
        print(f"  ERR {kw}: {d.get('message')}")
        return []
    res = d['data'].get('result', [])
    out = []
    for v in res:
        title = re.sub(r'<[^>]+>', '', v.get('title',''))
        out.append({
            'bvid': v.get('bvid',''),
            'title': title,
            'author': v.get('author',''),
            'play': v.get('play',0),
            'duration': v.get('duration',''),
            'pubdate': v.get('pubdate',0),
            'desc': v.get('description','')[:200],
            'kw': kw,
        })
    return out

# 关键词分组：3个方向 × 每组3个
KEYWORDS = [
    # 高低差
    '无畏契约 高低差 对枪',
    '无畏契约 上坡下坡 瞄准',
    'valorant 高低差 peek',
    # 穿墙
    '无畏契约 穿墙 穿点',
    '无畏契约 被穿死 怎么办',
    'valorant wallbang 防',
    # 靠墙/掩体
    '无畏契约 贴墙 peek',
    '无畏契约 掩体 对枪技巧',
    '无畏契约 优势枪位 站位',
]

all_videos = {}
for kw in KEYWORDS:
    print(f"搜索: {kw}")
    for page in [1, 2]:
        try:
            results = search(kw, page)
            for v in results:
                bvid = v['bvid']
                if bvid and bvid not in all_videos:
                    all_videos[bvid] = v
            time.sleep(1.5)
        except Exception as e:
            print(f"  ERR: {e}")
    print(f"  累计去重: {len(all_videos)}")

print(f"\n总去重视频数: {len(all_videos)}")

# 加权打分
def dur_to_sec(d):
    if not d: return 0
    parts = d.split(':')
    if len(parts) == 2: return int(parts[0])*60 + int(parts[1])
    if len(parts) == 3: return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
    return 0

W = [
    ('高低差', 12), ('上坡', 10), ('下坡', 10), ('peek', 8),
    ('穿墙', 12), ('穿点', 11), ('被穿', 10), ('wallbang', 10),
    ('贴墙', 10), ('掩体', 9), ('优势枪位', 10), ('站位', 8),
    ('对枪', 8), ('预瞄', 8), ('头线', 9), ('爆头线', 9),
    ('无畏契约', 3), ('valorant', 3), ('瓦', 2),
]
def score(v):
    t = (v['title'] + ' ' + v.get('desc','')).lower()
    s = sum(w for k,w in W if k.lower() in t)
    p = v.get('play') or 0
    s += 4 if p > 100000 else 3 if p > 30000 else 2 if p > 5000 else 0
    dur = dur_to_sec(v.get('duration',''))
    if dur < 60: s -= 3
    if dur > 600: s += 1
    return s

scored = sorted(all_videos.values(), key=lambda x: score(x), reverse=True)
for v in scored:
    v['_score'] = score(v)
    v['_dur_sec'] = dur_to_sec(v.get('duration',''))

# 保存全量
with open(os.path.join(OUT_DIR, '搜索结果-全量.json'), 'w', encoding='utf-8') as f:
    json.dump(scored, f, ensure_ascii=False, indent=2)

# 打印Top30
print("\n=== Top 30 ===")
for i, v in enumerate(scored[:30]):
    print(f"{i+1:2d}. [{v['_score']:3d}] {v['bvid']} | {v['play']:>8}播放 | {v['duration']:>6} | {v['title'][:40]} | {v['author']}")

# 精选Top15用于抓取
top15 = scored[:15]
with open(os.path.join(OUT_DIR, '精选列表.json'), 'w', encoding='utf-8') as f:
    json.dump(top15, f, ensure_ascii=False, indent=2)
print(f"\n精选 {len(top15)} 个视频用于字幕/评论抓取")
