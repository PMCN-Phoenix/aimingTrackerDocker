# -*- coding: utf-8 -*-
"""
BET脑耐力训练 - B站搜索与筛选
14组关键词 → 去重 → 相关度打分 → Top25
"""
import requests, hashlib, urllib.parse, re, json, time, sys, os, glob

OUTPUT_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q001-状态维持与注意力耐力\子问题\Q001.2-BET脑耐力训练实施方案\BET调研-B站原始数据"
COOKIE_DIR = r"D:\11.project\iwen-codex\bilibili-cookies"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

KEYWORDS = [
    "Brain Endurance Training",
    "BET 脑耐力训练",
    "脑耐力训练",
    "双任务训练 dual task",
    "认知负荷训练",
    "疲劳 认知表现",
    "Stroop 测试 训练",
    "2-back 工作记忆训练",
    "工作记忆训练 效果",
    "注意力耐力 训练",
    "认知耐力 提升",
    "cognitive endurance training",
    "dual task cognitive training",
    "brain training fatigue resistance",
]

def get_cookie():
    accounts = sorted(glob.glob(os.path.join(COOKIE_DIR, "account*.txt")))
    for acc in accounts:
        with open(acc, 'r', encoding='utf-8-sig') as f:
            cookie = f.read().strip()
        if cookie and 'SESSDATA=' in cookie:
            return cookie
    return None

def make_session(cookie):
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.bilibili.com/',
        'Cookie': cookie,
    })
    return s

def get_wbi_keys(s):
    nav = s.get('https://api.bilibili.com/x/web-interface/nav', timeout=20).json()
    wbi = nav['data']['wbi_img']
    img = wbi['img_url'].rsplit('/', 1)[-1].split('.')[0]
    sub = wbi['sub_url'].rsplit('/', 1)[-1].split('.')[0]
    return ''.join((img + sub)[i] for i in MIXIN)[:32]

def sign(params, mixin_key):
    p = dict(params)
    p['wts'] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p['w_rid'] = hashlib.md5((q + mixin_key).encode()).hexdigest()
    return p

def search_keyword(s, kw, mixin_key):
    all_results = []
    for page in range(1, 3):
        try:
            p = sign({'search_type': 'video', 'keyword': kw, 'page': page, 'page_size': 30}, mixin_key)
            res = s.get('https://api.bilibili.com/x/web-interface/wbi/search/type',
                       params=p, timeout=25).json()
            if res.get('code') != 0:
                print(f"  搜索 '{kw}' 第{page}页 code={res.get('code')}")
                break
            results = res.get('data', {}).get('result', [])
            if not results:
                break
            for v in results:
                title = re.sub(r'<[^>]+>', '', v.get('title', ''))
                dur = v.get('duration', '0:0')
                parts = dur.split(':')
                if len(parts) == 2:
                    dur_s = int(parts[0]) * 60 + int(parts[1])
                elif len(parts) == 3:
                    dur_s = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                else:
                    dur_s = 0
                all_results.append({
                    'bvid': v.get('bvid', ''),
                    'title': title,
                    'author': v.get('author', ''),
                    'play': v.get('play', 0),
                    'duration': dur,
                    'dur_s': dur_s,
                    'pubdate': v.get('pubdate', 0),
                    'desc': v.get('description', ''),
                    'keyword': kw,
                })
            time.sleep(1.0)
        except Exception as e:
            print(f"  搜索 '{kw}' 第{page}页异常: {e}")
            break
    return all_results

def score_video(v):
    t = (v['title'] or '') + ' ' + (v.get('desc') or '')
    s = 0.0
    for k, w in [('brain endurance', 10), ('BET', 8), ('脑耐力', 10), ('认知耐力', 8),
                 ('dual task', 8), ('双任务', 8), ('认知负荷', 7), ('stroop', 7),
                 ('2-back', 7), ('工作记忆', 6), ('n-back', 6), ('注意力耐力', 7),
                 ('疲劳', 5), ('认知表现', 6), ('cognitive', 4), ('endurance', 5),
                 ('训练', 3), ('提升', 2), ('方法', 2), ('科学', 2)]:
        if k.lower() in t.lower():
            s += w
    p = v.get('play') or 0
    if p > 500000: s += 3
    elif p > 100000: s += 2
    elif p > 30000: s += 1
    elif p > 0: s += 0.5
    else: s -= 1.5
    if v['dur_s'] < 60: s -= 1
    if v['dur_s'] > 600: s += 1
    return s

def main():
    print("=" * 60)
    print("BET脑耐力训练 - B站搜索与筛选")
    print("=" * 60)

    cookie = get_cookie()
    if not cookie:
        print("ERROR: 无有效 Cookie")
        sys.exit(1)
    print("✓ Cookie 获取成功")

    s = make_session(cookie)
    nav = s.get('https://api.bilibili.com/x/web-interface/nav', timeout=20).json()
    print(f"✓ 登录: {nav['data'].get('uname')} (isLogin={nav['data'].get('isLogin')})")

    mixin_key = get_wbi_keys(s)
    print("✓ wbi key 获取成功")

    all_videos = {}
    for i, kw in enumerate(KEYWORDS):
        print(f"\n[{i+1}/{len(KEYWORDS)}] 搜索: {kw}")
        results = search_keyword(s, kw, mixin_key)
        print(f"  找到 {len(results)} 条")
        for v in results:
            bvid = v['bvid']
            if bvid not in all_videos:
                all_videos[bvid] = v
        time.sleep(1.5)

    print(f"\n去重后共 {len(all_videos)} 个视频")

    scored = []
    for bvid, v in all_videos.items():
        v['score'] = score_video(v)
        scored.append(v)
    scored.sort(key=lambda x: x['score'], reverse=True)

    print("\n" + "=" * 60)
    print("Top 40 候选视频")
    print("=" * 60)
    for i, v in enumerate(scored[:40]):
        print(f"{i+1:2d}. [{v['score']:5.1f}] {v['title'][:42]:42s} | {v['author'][:14]:14s} | 播放:{v['play']:>8} | {v['duration']:>6} | {v['bvid']}")

    with open(os.path.join(OUTPUT_DIR, '相关视频搜索清单.json'), 'w', encoding='utf-8') as f:
        json.dump({'keywords': KEYWORDS, 'total_unique': len(all_videos),
                   'search_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                   'all_videos': scored}, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 搜索清单已保存")

    top_n = 25
    selected = scored[:top_n]
    with open(os.path.join(OUTPUT_DIR, '精选视频列表.json'), 'w', encoding='utf-8') as f:
        json.dump(selected, f, ensure_ascii=False, indent=2)
    print(f"✓ 选定 Top {top_n} 进入评论+字幕抓取")

if __name__ == '__main__':
    main()
