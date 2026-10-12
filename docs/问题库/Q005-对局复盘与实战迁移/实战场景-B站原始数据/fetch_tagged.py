# -*- coding: utf-8 -*-
"""抓取精选视频的字幕和评论 - 被击中减速/急停专题"""
import requests, re, json, time, hashlib, urllib.parse, os

COOKIE_FILE = r"D:\11.project\iwen-codex\bilibili-cookies\account1.txt"
OUT_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-B站原始数据"
SUB_DIR = os.path.join(OUT_DIR, "字幕")
CMT_DIR = os.path.join(OUT_DIR, "评论")
os.makedirs(SUB_DIR, exist_ok=True)
os.makedirs(CMT_DIR, exist_ok=True)

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

# 精选12个（跳过已抓过的BV1EthLzMEKw）
BVIDS = [
    "BV14QpDzFEUi",  # 枪法到意识全概括
    "BV1quQiYPECg",  # 最容易的急停方式
    "BV1qc411L7MY",  # 即松即停（26万播放）
    "BV1ca411w762",  # skillcap移动中穿插射击
    "BV1XM4m1z7pS",  # 开枪必定急停改键
    "BV1GKFvzKEwU",  # VCT公开课移动瞄准急停开枪
    "BV11fbv6DEJf",  # 神三移动瞄准急停开枪训练
    "BV1MY4y1H79Z",  # 大东彦最全急停教学（63万播放）
    "BV1ts4y1E7Zm",  # Woohoojin移动才是问题根源
    "BV1HUk4BXEdn",  # 你开不出枪？是你太早开枪（直接命中！）
    "BV11fbv6DE3K",  # 缓解拉枪开枪太着急
    "BV1yX4y1k7H7",  # Woohoojin不要再像noob一样移动（60万播放）
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

def sign_params(s, params, mixin):
    p = dict(params)
    p['wts'] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p['w_rid'] = hashlib.md5((q+mixin).encode()).hexdigest()
    return p

def get_video_info(s, bvid):
    r = s.get(f'https://www.bilibili.com/video/{bvid}/', timeout=25)
    t = r.text
    m = re.search(r'window\.__INITIAL_STATE__=(.*?);\(function', t, re.S)
    if not m:
        m = re.search(r'window\.__INITIAL_STATE__=(.*?);\s*</script>', t, re.S)
    d = json.loads(m.group(1))
    v = d['videoData']
    return v['aid'], v['cid'], v['title'], v['owner']['name'], v['duration']

def get_subtitle(s, bvid, cid, mixin):
    p = sign_params(s, {'bvid': bvid, 'cid': cid}, mixin)
    r = s.get('https://api.bilibili.com/x/player/wbi/v2', params=p, timeout=20)
    d = r.json()
    subs = d.get('data',{}).get('subtitle',{}).get('subtitles',[])
    if not subs:
        return None
    url = subs[0]['subtitle_url']
    if url.startswith('//'): url = 'https:' + url
    r2 = s.get(url, timeout=20)
    return r2.json()

def get_comments(s, aid):
    all_comments = []
    for pn in range(1, 6):
        r = s.get('https://api.bilibili.com/x/v2/reply',
                  params={'oid': aid, 'type': 1, 'pn': pn, 'ps': 20, 'sort': 2}, timeout=20)
        d = r.json()
        if d.get('code') != 0: break
        replies = d.get('data',{}).get('replies',[])
        if not replies: break
        for c in replies:
            all_comments.append({
                'message': c.get('content',{}).get('message',''),
                'like': c.get('like',0),
                'rcount': c.get('rcount',0),
                'subs': [{'message': sc.get('content',{}).get('message',''), 'like': sc.get('like',0)}
                         for sc in (c.get('replies') or [])[:5]],
            })
        time.sleep(1.2)
    return all_comments

s = get_session()
mixin = get_wbi(s)

results = []
for i, bvid in enumerate(BVIDS):
    print(f"\n[{i+1}/{len(BVIDS)}] {bvid}")
    try:
        aid, cid, title, author, duration = get_video_info(s, bvid)
        print(f"  {title[:40]} | {author} | {duration}s")
        
        sub = get_subtitle(s, bvid, cid, mixin)
        if sub:
            with open(os.path.join(SUB_DIR, f"{bvid}.json"), 'w', encoding='utf-8') as f:
                json.dump(sub, f, ensure_ascii=False, indent=2)
            text = '\n'.join(f"[{x['from']:.0f}s] {x['content']}" for x in sub.get('body',[]))
            with open(os.path.join(SUB_DIR, f"{bvid}.txt"), 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"  字幕: {len(sub.get('body',[]))} 段")
        else:
            print(f"  字幕: 无AI字幕")
        
        comments = get_comments(s, aid)
        with open(os.path.join(CMT_DIR, f"{bvid}.json"), 'w', encoding='utf-8') as f:
            json.dump(comments, f, ensure_ascii=False, indent=2)
        print(f"  评论: {len(comments)} 条")
        
        results.append({'bvid': bvid, 'title': title, 'author': author, 
                       'duration': duration, 'has_sub': sub is not None, 'comments': len(comments)})
        time.sleep(1)
    except Exception as e:
        print(f"  ERR: {e}")
        results.append({'bvid': bvid, 'error': str(e)})

with open(os.path.join(OUT_DIR, '抓取结果-被击中减速.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n=== 抓取完成 ===")
for r in results:
    if 'error' in r:
        print(f"  {r['bvid']}: ERR {r['error']}")
    else:
        print(f"  {r['bvid']}: 字幕={'Y' if r['has_sub'] else 'N'} 评论={r['comments']} | {r['title'][:30]}")
