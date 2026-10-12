# -*- coding: utf-8 -*-
"""
Q001 第二轮调研抓取：
1. 对 25 个精选视频拿 aid/cid（网页HTML __INITIAL_STATE__）
2. 补抓缺字幕的 14 个视频（wbi /x/player/wbi/v2）
3. 抓全部 25 个视频评论（wbi /x/v2/reply/wbi/main 主评论 + /x/v2/reply/wbi/reply 楼中楼）
走 Cookie 池轮询，412 自动切换，请求间隔 1.2-2s
"""
import requests, hashlib, urllib.parse, re, json, time, os, sys, glob

OUTPUT_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q001-状态维持与注意力耐力\专注力训练-B站原始数据"
SUBTITLE_DIR = os.path.join(OUTPUT_DIR, "字幕")
COMMENT_DIR = os.path.join(OUTPUT_DIR, "评论")
os.makedirs(SUBTITLE_DIR, exist_ok=True)
os.makedirs(COMMENT_DIR, exist_ok=True)

sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


class Fetcher:
    def __init__(self):
        self.pool = BiliCookiePool()
        self.s = None
        self.mixin_key = None
        self._new_session()

    def _new_session(self):
        cookie = self.pool.get_cookie()
        self.s = requests.Session()
        self.s.headers.update({'User-Agent': UA, 'Referer': 'https://www.bilibili.com/'})
        self.s.headers['Cookie'] = cookie
        # 拿 wbi key
        nav = self.s.get('https://api.bilibili.com/x/web-interface/nav', timeout=20).json()
        wbi = nav['data']['wbi_img']
        img = wbi['img_url'].rsplit('/', 1)[-1].split('.')[0]
        sub = wbi['sub_url'].rsplit('/', 1)[-1].split('.')[0]
        self.mixin_key = ''.join((img + sub)[i] for i in MIXIN)[:32]
        uname = nav['data'].get('uname', '?')
        print(f"  [session] 切换账号: {uname}")

    def sign(self, params):
        p = dict(params)
        p['wts'] = str(int(time.time()))
        q = urllib.parse.urlencode(sorted(p.items()))
        p['w_rid'] = hashlib.md5((q + self.mixin_key).encode()).hexdigest()
        return p

    def get(self, url, params=None, referer=None, retries=3):
        """带 412 切换账号的 GET"""
        headers = {}
        if referer:
            headers['Referer'] = referer
        for attempt in range(retries):
            try:
                r = self.s.get(url, params=params, headers=headers, timeout=25)
                if r.status_code == 412 or '"code":-412' in r.text:
                    print(f"    [412] 切换账号... (attempt {attempt+1})")
                    self.pool.report_412()
                    self._new_session()
                    time.sleep(3)
                    continue
                self.pool.report_success()
                return r
            except Exception as e:
                print(f"    [get异常] {e}, retry {attempt+1}")
                time.sleep(3)
        return None


def get_video_info(f, bvid):
    r = f.get(f'https://www.bilibili.com/video/{bvid}/')
    if not r:
        return None
    t = r.text
    m = (re.search(r'window\.__INITIAL_STATE__=(.*?);\(function', t, re.S)
         or re.search(r'window\.__INITIAL_STATE__=(.*?);\s*</script>', t, re.S))
    if not m:
        return None
    try:
        v = json.loads(m.group(1))['videoData']
    except Exception:
        return None
    return {
        'aid': v['aid'],
        'cid': v['cid'],
        'title': v['title'],
        'owner': v['owner']['name'],
        'duration': v['duration'],
        'desc': (v.get('desc') or '')[:600],
    }


def get_subtitle(f, bvid, cid):
    q = f.sign({'bvid': bvid, 'cid': str(cid), 'web_location': '333.1007'})
    r = f.get('https://api.bilibili.com/x/player/wbi/v2', params=q,
              referer=f'https://www.bilibili.com/video/{bvid}/')
    if not r:
        return None, '请求失败'
    d = r.json()
    subs = ((d.get('data') or {}).get('subtitle') or {}).get('subtitles') or []
    if not subs:
        return None, '无AI字幕'
    pick = None
    for pref in ['zh-Hans', 'zh-CN', 'zh', 'ai-zh', 'en-US', 'en']:
        pick = next((x for x in subs if x.get('lan') == pref), None)
        if pick:
            break
    if not pick:
        pick = subs[0]
    u = pick.get('subtitle_url') or ''
    if u.startswith('//'):
        u = 'https:' + u
    if not u:
        return None, 'subtitle_url为空'
    for attempt in range(4):
        body_r = f.get(u, referer=f'https://www.bilibili.com/video/{bvid}/')
        if body_r:
            try:
                body = body_r.json().get('body')
                if body:
                    return body, pick.get('lan', 'unknown')
            except Exception:
                pass
        time.sleep(3)
    return None, '字幕正文为空'


def get_comments(f, bvid, aid, max_main=3):
    """wbi/main 主评论（热度排序）+ 楼中楼 wbi/reply。每视频抓 max_main 页主评论=60条上限，热门楼中楼全抓第一页"""
    main_comments = []
    total = 0
    nxt = 0
    for pn in range(1, max_main + 1):
        q = f.sign({'oid': aid, 'type': 1, 'mode': 3, 'next': nxt, 'ps': 20,
                    'web_location': '1315875'})
        r = f.get('https://api.bilibili.com/x/v2/reply/wbi/main', params=q,
                  referer=f'https://www.bilibili.com/video/{bvid}/')
        if not r:
            break
        d = r.json()
        if d.get('code') != 0:
            print(f"    评论page{pn} code={d.get('code')} msg={d.get('message')}")
            break
        dd = d.get('data') or {}
        reps = dd.get('replies') or []
        cursor = dd.get('cursor') or {}
        total = cursor.get('all_count', dd.get('page', {}).get('count', 0)) or 0
        if not reps:
            break
        for rep in reps:
            c = {
                'uname': rep['member']['uname'],
                'like': rep['like'],
                'rcount': rep['rcount'],
                'rpid': rep['rpid'],
                'message': rep['content']['message'],
                'subs': [],
            }
            # 楼中楼：只对 rcount>0 的热门主评论抓第一页
            if rep['rcount'] and rep['rcount'] > 0:
                sq = f.sign({'oid': aid, 'type': 1, 'root': rep['rpid'], 'ps': 20, 'pn': 1})
                sr = f.get('https://api.bilibili.com/x/v2/reply/wbi/reply', params=sq,
                           referer=f'https://www.bilibili.com/video/{bvid}/')
                if sr:
                    try:
                        subs = (sr.json().get('data') or {}).get('replies') or []
                        for sub in subs:
                            c['subs'].append({
                                'uname': sub['member']['uname'],
                                'like': sub['like'],
                                'message': sub['content']['message'],
                            })
                    except Exception:
                        pass
                time.sleep(1.2)
            main_comments.append(c)
        if cursor.get('is_end'):
            break
        nxt = cursor.get('next', 0)
        time.sleep(1.5)
    return main_comments, total


def main():
    print("=" * 60)
    with open(os.path.join(OUTPUT_DIR, '精选视频列表.json'), 'r', encoding='utf-8') as fp:
        selected = json.load(fp)

    f = Fetcher()
    print(f"待处理视频: {len(selected)}")

    # 已有字幕
    have_sub = set(os.path.basename(p).replace('.json', '')
                   for p in glob.glob(os.path.join(SUBTITLE_DIR, '*.json')))
    print(f"已有字幕: {len(have_sub)} 个")

    # 评论元信息文件
    meta_path = os.path.join(OUTPUT_DIR, '视频元信息.json')
    meta = {}
    if os.path.exists(meta_path):
        meta = json.load(open(meta_path, 'r', encoding='utf-8'))

    for i, v in enumerate(selected):
        bvid = v['bvid']
        print(f"\n[{i+1}/{len(selected)}] {v['title'][:30]} ({bvid})")

        # 1. 视频信息（如已有缓存则跳过）
        if bvid not in meta:
            info = get_video_info(f, bvid)
            if not info:
                print("  !! 无法获取视频信息")
                meta[bvid] = {'title': v['title'], 'error': 'no_info'}
                continue
            meta[bvid] = info
            json.dump(meta, open(meta_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
            time.sleep(1.5)
        info = meta[bvid]
        if 'aid' not in info:
            print("  !! 元信息缺失，跳过")
            continue
        print(f"  aid={info['aid']} dur={info['duration']}s")

        # 2. 字幕（缺则补）
        if bvid not in have_sub:
            body, status = get_subtitle(f, bvid, info['cid'])
            if body:
                json.dump(body, open(os.path.join(SUBTITLE_DIR, f'{bvid}.json'), 'w', encoding='utf-8'),
                          ensure_ascii=False, indent=2)
                last_to = max((seg.get('to', 0) for seg in body), default=0)
                cov = last_to / info['duration'] if info['duration'] else 0
                print(f"  字幕✓ {len(body)}段 覆盖{cov:.0%} ({status})")
            else:
                print(f"  字幕✗ {status}")
                # 写一个标记文件
                json.dump({'status': status}, open(os.path.join(SUBTITLE_DIR, f'{bvid}.noml.txt'), 'w', encoding='utf-8'))
            time.sleep(1.5)

        # 3. 评论
        cpath = os.path.join(COMMENT_DIR, f'{bvid}.json')
        if os.path.exists(cpath):
            print(f"  评论✓ 已存在")
            continue
        comments, total = get_comments(f, bvid, info['aid'])
        out = {
            'title': info['title'], 'aid': info['aid'], 'owner': info['owner'],
            'duration': info['duration'], 'desc': info['desc'],
            'comment_total': total, 'fetched': len(comments),
            'comments': comments,
        }
        json.dump(out, open(cpath, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f"  评论✓ {len(comments)}/{total}")
        time.sleep(1.5)

    print("\n=== 完成 ===")


if __name__ == '__main__':
    main()
