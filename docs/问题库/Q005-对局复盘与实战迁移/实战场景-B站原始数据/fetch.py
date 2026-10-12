# -*- coding: utf-8 -*-
"""抓取精选视频的字幕和评论"""
import requests, re, json, time, hashlib, urllib.parse, os

COOKIE_FILE = r"D:\11.project\iwen-codex\bilibili-cookies\account1.txt"
OUT_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-B站原始数据"
SUB_DIR = os.path.join(OUT_DIR, "字幕")
CMT_DIR = os.path.join(OUT_DIR, "评论")
os.makedirs(SUB_DIR, exist_ok=True)
os.makedirs(CMT_DIR, exist_ok=True)

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

# 精选12个
BVIDS = [
    "BV1RezPYCESM",  # 身位控制/贴墙大拉/高打低
    "BV1eqdSBiE2i",  # 架枪不架高低差（职业教练RajA）
    "BV1EthLzMEKw",  # 大拉peek/预瞄/选择枪位
    "BV1P73G6zE1E",  # 架好头线为什么被秒
    "BV1Chjb6aEt6",  # 掩体后劣势对枪优化
    "BV1mD4y1w7VH",  # 穿墙机制讲解
    "BV1Ua411Z71q",  # 穿墙机制/材质
    "BV1v7hv6iE3J",  # 穿墙点爆头线
    "BV1SW4y1d7PP",  # peek/急停/爆头线进阶
    "BV1ZH9cBvEUU",  # 为什么你的peek这么烂（VEI_J）
    "BV1BSh5zPE2d",  # peek完回缩/贴墙大拉
    "BV182ZTB7Eco",  # 几乎从不输掉对枪（Haeyoday）
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
        
        # 字幕
        sub = get_subtitle(s, bvid, cid, mixin)
        if sub:
            with open(os.path.join(SUB_DIR, f"{bvid}.json"), 'w', encoding='utf-8') as f:
                json.dump(sub, f, ensure_ascii=False, indent=2)
            # 提取纯文本
            text = '\n'.join(f"[{x['from']:.0f}s] {x['content']}" for x in sub.get('body',[]))
            with open(os.path.join(SUB_DIR, f"{bvid}.txt"), 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"  字幕: {len(sub.get('body',[]))} 段")
        else:
            print(f"  字幕: 无AI字幕")
        
        # 评论
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

with open(os.path.join(OUT_DIR, '抓取结果.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n=== 抓取完成 ===")
for r in results:
    if 'error' in r:
        print(f"  {r['bvid']}: ERR {r['error']}")
    else:
        print(f"  {r['bvid']}: 字幕={'Y' if r['has_sub'] else 'N'} 评论={r['comments']} | {r['title'][:30]}")
