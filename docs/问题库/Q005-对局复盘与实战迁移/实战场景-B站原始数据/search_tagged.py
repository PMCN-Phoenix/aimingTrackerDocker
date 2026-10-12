# -*- coding: utf-8 -*-
"""B站搜索：被击中减速/拉枪被点开不出枪"""
import requests, json, time, hashlib, urllib.parse, re, os

COOKIE_FILE = r"D:\11.project\iwen-codex\bilibili-cookies\account1.txt"
OUT_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-B站原始数据"
os.makedirs(OUT_DIR, exist_ok=True)

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

KEYWORDS = [
    "无畏契约 被击中减速 急停",
    "无畏契约 拉枪 被点 开不出枪",
    "无畏契约 移动中开枪 急停技巧",
    "无畏契约 peek 被减速 反打",
    "无畏契约 急停 被打 移动惩罚",
    "valorant tagged movement penalty 急停",
    "无畏契约 对枪 移动 开枪时机",
    "无畏契约 大拉 被点 怎么反打",
    "无畏契约 急停教学 移动射击",
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

# 加权打分
W = [('急停',12),('减速',11),('被点',10),('被击中',10),('移动',8),('开枪',8),
     ('peek',9),('大拉',9),('反打',9),('对枪',8),('tagged',8),('movement',7),
     ('惩罚',7),('开不出枪',10),('拉枪',8),('射击',6)]
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
with open(os.path.join(OUT_DIR, '搜索结果-被击中减速.json'), 'w', encoding='utf-8') as f:
    json.dump(list(all_videos.values()), f, ensure_ascii=False, indent=2)
with open(os.path.join(OUT_DIR, '精选列表-被击中减速.json'), 'w', encoding='utf-8') as f:
    json.dump(top15, f, ensure_ascii=False, indent=2)
print(f"\n精选 {len(top15)} 个视频用于字幕/评论抓取")
