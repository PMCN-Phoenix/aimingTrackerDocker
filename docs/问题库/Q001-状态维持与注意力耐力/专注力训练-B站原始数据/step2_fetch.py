# -*- coding: utf-8 -*-
"""
B站专注力训练主题调研 - 评论+字幕抓取阶段
按 SOP：拿 aid/cid（网页HTML）→ 抓评论（主+楼中楼）→ 抓字幕（wbi）
"""
import requests, hashlib, urllib.parse, re, json, time, sys, os, glob

# 配置
OUTPUT_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q001-状态维持与注意力耐力\专注力训练-B站原始数据"
COOKIE_DIR = r"D:\11.project\iwen-codex\bilibili-cookies"
SUBTITLE_DIR = os.path.join(OUTPUT_DIR, "字幕")
os.makedirs(SUBTITLE_DIR, exist_ok=True)

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

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

def get_video_info(s, bvid):
    """从网页 HTML 拿 aid/cid（避免 412）"""
    try:
        r = s.get(f'https://www.bilibili.com/video/{bvid}/', timeout=25)
        t = r.text
        m = (re.search(r'window\.__INITIAL_STATE__=(.*?);\(function', t, re.S)
             or re.search(r'window\.__INITIAL_STATE__=(.*?);\s*</script>', t, re.S))
        if not m:
            print(f"  [{bvid}] 无法解析 __INITIAL_STATE__")
            return None
        v = json.loads(m.group(1))['videoData']
        return {
            'aid': v['aid'],
            'cid': v['cid'],
            'title': v['title'],
            'owner': v['owner']['name'],
            'duration': v['duration'],
            'desc': v.get('desc', '')[:500],
            'pages': [{'cid': p['cid'], 'part': p.get('part', '')} for p in v.get('pages', [])],
        }
    except Exception as e:
        print(f"  [{bvid}] 获取视频信息异常: {e}")
        return None

def get_comments(s, bvid, aid, max_pages=8):
    """抓主评论 + 楼中楼"""
    all_comments = []
    total_count = 0
    for pn in range(1, max_pages + 1):
        try:
            d = s.get('https://api.bilibili.com/x/v2/reply',
                     params={'oid': aid, 'type': 1, 'pn': pn, 'ps': 20, 'sort': 2},
                     headers={'Referer': f'https://www.bilibili.com/video/{bvid}/'},
                     timeout=25).json()
            if d.get('code') != 0:
                print(f"    评论第{pn}页 code={d.get('code')}")
                break
            dd = d.get('data') or {}
            reps = dd.get('replies') or []
            if not reps:
                break
            total_count = (dd.get('page') or {}).get('count', 0)
            for rep in reps:
                comment = {
                    'uname': rep['member']['uname'],
                    'like': rep['like'],
                    'rcount': rep['rcount'],
                    'rpid': rep['rpid'],
                    'message': rep['content']['message'],
                    'subs': [],
                }
                # 楼中楼
                if rep['rcount'] > 0:
                    try:
                        d2 = s.get('https://api.bilibili.com/x/v2/reply/reply',
                                  params={'oid': aid, 'type': 1, 'root': rep['rpid'], 'pn': 1, 'ps': 20},
                                  headers={'Referer': f'https://www.bilibili.com/video/{bvid}/'},
                                  timeout=25).json()
                        subs = (d2.get('data') or {}).get('replies') or []
                        for sub in subs:
                            comment['subs'].append({
                                'uname': sub['member']['uname'],
                                'like': sub['like'],
                                'message': sub['content']['message'],
                            })
                        time.sleep(0.8)
                    except Exception as e:
                        print(f"    楼中楼异常 rpid={rep['rpid']}: {e}")
                all_comments.append(comment)
            if len(all_comments) >= total_count:
                break
            time.sleep(1.2)
        except Exception as e:
            print(f"    评论第{pn}页异常: {e}")
            break
    return all_comments, total_count

def get_subtitle(s, bvid, cid, mixin_key):
    """抓 AI 字幕（wbi 接口）"""
    try:
        q = sign({'bvid': bvid, 'cid': str(cid), 'web_location': '333.1007'}, mixin_key)
        d = s.get('https://api.bilibili.com/x/player/wbi/v2', params=q,
                 headers={'Referer': f'https://www.bilibili.com/video/{bvid}/'}, timeout=20).json()
        subs = ((d.get('data') or {}).get('subtitle') or {}).get('subtitles') or []
        if not subs:
            return None, '无字幕'
        # 语言优先级
        pick = None
        for pref in ['zh-Hans', 'zh-CN', 'zh', 'ai-zh', 'en']:
            pick = next((x for x in subs if x.get('lan') == pref), None)
            if pick:
                break
        if not pick:
            pick = subs[0]
        u = pick['subtitle_url']
        if u.startswith('//'):
            u = 'https:' + u
        # 重试机制
        for attempt in range(4):
            body = s.get(u, headers={'Referer': f'https://www.bilibili.com/video/{bvid}/'}, timeout=25).json()
            if body.get('body'):
                return body['body'], pick.get('lan', 'unknown')
            time.sleep(3)
        return None, '字幕为空'
    except Exception as e:
        return None, f'异常: {e}'

def main():
    print("=" * 60)
    print("B站专注力训练调研 - 评论+字幕抓取")
    print("=" * 60)

    # 读取精选列表
    with open(os.path.join(OUTPUT_DIR, '精选视频列表.json'), 'r', encoding='utf-8') as f:
        selected = json.load(f)
    print(f"待抓取视频: {len(selected)} 个")

    # Cookie + session
    cookie = get_cookie()
    s = make_session(cookie)
    nav = s.get('https://api.bilibili.com/x/web-interface/nav', timeout=20).json()
    print(f"登录: {nav['data'].get('uname')} (isLogin={nav['data'].get('isLogin')})")
    mixin_key = get_wbi_keys(s)

    # 结果存储
    results = {}
    comment_count_total = 0
    subtitle_count = 0

    for i, v in enumerate(selected):
        bvid = v['bvid']
        title = v['title'][:35]
        print(f"\n[{i+1}/{len(selected)}] {title} ({bvid})")

        # 1. 拿 aid/cid
        info = get_video_info(s, bvid)
        if not info:
            print(f"  跳过：无法获取视频信息")
            continue
        print(f"  aid={info['aid']} cid={info['cid']} 时长={info['duration']}s")

        # 2. 抓评论
        comments, total = get_comments(s, bvid, info['aid'])
        comment_count_total += len(comments)
        print(f"  评论: {len(comments)}/{total} 条")

        # 3. 抓字幕
        subtitle_body, sub_status = get_subtitle(s, bvid, info['cid'], mixin_key)
        if subtitle_body:
            subtitle_count += 1
            # 保存字幕
            with open(os.path.join(SUBTITLE_DIR, f"{bvid}.json"), 'w', encoding='utf-8') as f:
                json.dump(subtitle_body, f, ensure_ascii=False, indent=2)
            # 计算覆盖率
            last_to = max((seg.get('to', 0) for seg in subtitle_body), default=0)
            coverage = last_to / info['duration'] if info['duration'] > 0 else 0
            print(f"  字幕: {len(subtitle_body)}段, 覆盖 {coverage:.1%} ({sub_status})")
        else:
            print(f"  字幕: {sub_status}")

        # 存储结果
        results[bvid] = {
            'title': info['title'],
            'aid': info['aid'],
            'cid': info['cid'],
            'owner': info['owner'],
            'duration': info['duration'],
            'desc': info['desc'],
            'comment_total': total,
            'comments_fetched': len(comments),
            'comments': comments,
            'subtitle_status': sub_status,
            'subtitle_segments': len(subtitle_body) if subtitle_body else 0,
            'score': v.get('score', 0),
            'play': v.get('play', 0),
        }
        time.sleep(1.0)

    # 保存评论结果
    with open(os.path.join(OUTPUT_DIR, '视频评论.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"抓取完成: {len(results)} 个视频")
    print(f"评论总数: {comment_count_total} 条")
    print(f"字幕获取: {subtitle_count}/{len(results)} 个")
    print(f"原始数据: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == '__main__':
    main()
