# -*- coding: utf-8 -*-
"""B站搜索：残局1v1掩体/箱体处理"""
import requests, json, time, hashlib, urllib.parse, re, os

COOKIE_FILE = r"D:\11.project\iwen-codex\bilibili-cookies\account1.txt"
OUT_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-B站原始数据"
os.makedirs(OUT_DIR, exist_ok=True)

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

KEYWORDS = [
    "无畏契约 残局 1v1 掩体 处理",
    "无畏契约 残局 箱体 对枪技巧",
    "无畏契约 锁定位置 怎么打 残局",
    "无畏契约 残局 心态 决策 1v1",
    "无畏契约 假动作 骗枪 残局",
    "无畏契约 掩体 peek 残局 博弈",
    "valorant 1v1 clutch box positioning",
    "无畏契约 残局 思路 教学",
    "无畏契约 1v1 对枪 掩体后",
]

def get_session():
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    cookie = open(COOKIE_FILE, encoding='utf-8-sig').read().strip()
    s.headers['Cookie'] = cookie
    return s

def get_wbi(s):
    nav = s.get('https://api.bilibili.com/x/web-interface/nav', timeout=20).json()
    wbi = nav['data']['wbi_img']
    img = wbi['img_url'].rsplit('/',1)[-1].split('.')[0]
    sub = wbi['sub_url'].rsplit('/',1)[-1].split('.')[0]
    return ''.join((img+sub)[i] for i in MIXIN)[:32]

def sign_params(params, mixin):
    p = dict(params)
    p['wts'] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p['w_rid'] = hashlib.md5((q+mixin).encode()).hexdigest()
    return p

def parse_dur(s):
    if not s: return 0
    parts = s.split(':')
    if len(parts) == 2: return int(parts[0])*60 + int(parts[1])
    if len(parts) == 3: return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
    return 0

s = get_session()
mixin = get_wbi(s)

all_videos = {}
for kw in KEYWORDS:
    print(f"搜索: {kw}")
    for page in range(1, 3):
        p = sign_params({'search_type': 'video', 'keyword': kw, 'page': page, 'page_size': 30}, mixin)
        r = s.get('https://api.bilibili.com/x/web-interface/wbi/search/type', params=p, timeout=25)
        try:
            res = r.json().get('data',{}).get('result',[])
        except:
            res = []
        for v in res:
            bvid = v.get('bvid','')
            if not bvid or bvid in all_videos: continue
            title = re.sub(r'<[^>]+>','', v.get('title',''))
            all_videos[bvid] = {
                'bvid': bvid, 'title': title,
                'author': v.get('author',''),
                'play': v.get('play',0), 'duration': parse_dur(v.get('duration','')),
                'pubdate': v.get('pubdate',0), 'desc': v.get('description','')[:200],
                'keyword': kw,
            }
        time.sleep(0.8)
    print(f"  累计去重: {len(all_videos)}")

print(f"\n总去重视频数: {len(all_videos)}")

W = [('残局',12),('1v1',11),('clutch',10),('掩体',10),('箱体',10),('箱',8),
     ('假动作',9),('骗枪',9),('心态',8),('决策',8),('思路',7),('锁定',8),
     ('位置',6),('peek',8),('博弈',8),('对枪',7),('处理',6),('1打1',9),
     ('残局教学',11),('残局思路',10),('1v1教学',10)]
def score(v):
    t = ((v['title'] or '') + ' ' + (v.get('desc') or '')).lower()
    s = sum(w for k,w in W if k.lower() in t)
    p = v.get('play') or 0
    s += 4 if p > 500000 else 3 if p > 150000 else 2 if p > 40000 else 1 if p > 10000 else -2
    if v['duration'] < 150: s -= 3
    if v['duration'] > 600: s += 1
    return s

ranked = sorted(all_videos.values(), key=score, reverse=True)
print("\n=== Top 25 ===")
for i, v in enumerate(ranked[:25]):
    print(f" {i+1:2d}. [{score(v):3d}] {v['bvid']} | {v['play']:>7}播放 | {v['duration']//60}:{v['duration']%60:02d} | {v['title'][:45]} | {v['author']}")

top15 = ranked[:15]
with open(os.path.join(OUT_DIR, '搜索结果-残局掩体.json'), 'w', encoding='utf-8') as f:
    json.dump(list(all_videos.values()), f, ensure_ascii=False, indent=2)
with open(os.path.join(OUT_DIR, '精选列表-残局掩体.json'), 'w', encoding='utf-8') as f:
    json.dump(top15, f, ensure_ascii=False, indent=2)
print(f"\n精选 {len(top15)} 个视频用于字幕/评论抓取")
