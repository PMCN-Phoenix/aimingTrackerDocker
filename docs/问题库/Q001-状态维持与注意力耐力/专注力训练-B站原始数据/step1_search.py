# -*- coding: utf-8 -*-
"""
B站专注力训练主题调研 - 搜索与筛选阶段
按 SOP：wbi 签名搜索 → 多关键词去重 → 相关度打分 → top 30
"""
import requests, hashlib, urllib.parse, re, json, time, sys, os

# 配置
PYTHON_PATH = r"D:\6_code\13_python\1_python3.11.0\python.exe"
OUTPUT_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q001-状态维持与注意力耐力\专注力训练-B站原始数据"
COOKIE_DIR = r"D:\11.project\iwen-codex\bilibili-cookies"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# MIXIN 表（wbi 签名用）
MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

# 关键词（14 组，中英 + 换说法 + 场景词）
KEYWORDS = [
    "专注力训练",
    "注意力训练",
    "专注力提升 方法",
    "注意力持久 训练",
    "冥想 专注力",
    "正念 注意力",
    "专注力 每日训练",
    "注意力 科学训练",
    "专注力 练习 有效",
    "注意力不集中 改善",
    "专注力 训练计划",
    "focus training daily",
    "attention span training",
    "mindfulness focus",
]

def get_cookie():
    """从 Cookie 池取一个有效 Cookie"""
    import glob
    accounts = sorted(glob.glob(os.path.join(COOKIE_DIR, "account*.txt")))
    # 读第一个有效账号
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
    mixin = ''.join((img + sub)[i] for i in MIXIN)[:32]
    return mixin

def sign(params, mixin_key):
    p = dict(params)
    p['wts'] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p['w_rid'] = hashlib.md5((q + mixin_key).encode()).hexdigest()
    return p

def search_keyword(s, kw, mixin_key):
    """搜索单个关键词，返回视频列表"""
    all_results = []
    for page in range(1, 3):  # 前 2 页，60 条
        try:
            p = sign({'search_type': 'video', 'keyword': kw, 'page': page, 'page_size': 30}, mixin_key)
            res = s.get('https://api.bilibili.com/x/web-interface/wbi/search/type',
                       params=p, timeout=25).json()
            if res.get('code') != 0:
                print(f"  搜索 '{kw}' 第{page}页失败: code={res.get('code')} msg={res.get('message')}")
                break
            results = res.get('data', {}).get('result', [])
            if not results:
                break
            for v in results:
                # 清理标题中的 <em> 高亮
                title = re.sub(r'<[^>]+>', '', v.get('title', ''))
                # 时长转秒
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
    """相关度打分"""
    t = (v['title'] or '') + ' ' + (v.get('desc') or '')
    s = 0.0
    # 主题关键词权重
    for k, w in [('专注力', 8), ('注意力', 8), ('专注', 5), ('注意', 4),
                 ('冥想', 6), ('正念', 6), ('mindfulness', 5), ('focus', 4),
                 ('attention', 5), ('训练', 3), ('提升', 2), ('方法', 2),
                 ('每日', 2), ('科学', 2), ('持久', 3)]:
        if k.lower() in t.lower():
            s += w
    # 播放量加分
    p = v.get('play') or 0
    if p > 500000: s += 3
    elif p > 100000: s += 2
    elif p > 30000: s += 1
    elif p > 0: s += 0.5
    else: s -= 1.5
    # 太短减分
    if v['dur_s'] < 60: s -= 1
    # 太长加分（深度内容）
    if v['dur_s'] > 600: s += 1
    return s

def main():
    print("=" * 60)
    print("B站专注力训练调研 - 搜索与筛选")
    print("=" * 60)

    # 1. 获取 Cookie
    cookie = get_cookie()
    if not cookie:
        print("ERROR: 无法获取有效 Cookie")
        sys.exit(1)
    print("✓ Cookie 获取成功")

    s = make_session(cookie)

    # 验证登录
    nav = s.get('https://api.bilibili.com/x/web-interface/nav', timeout=20).json()
    print(f"✓ 登录状态: isLogin={nav['data'].get('isLogin')} uname={nav['data'].get('uname')}")

    # 2. 获取 wbi key
    mixin_key = get_wbi_keys(s)
    print(f"✓ wbi key 获取成功")

    # 3. 多关键词搜索
    all_videos = {}
    for i, kw in enumerate(KEYWORDS):
        print(f"\n[{i+1}/{len(KEYWORDS)}] 搜索: {kw}")
        results = search_keyword(s, kw, mixin_key)
        print(f"  找到 {len(results)} 条")
        for v in results:
            bvid = v['bvid']
            if bvid not in all_videos:
                all_videos[bvid] = v
            else:
                # 合并关键词来源
                if kw not in all_videos[bvid].get('keywords', []):
                    all_videos[bvid].setdefault('keywords', []).append(kw)
        time.sleep(1.5)

    print(f"\n去重后共 {len(all_videos)} 个视频")

    # 4. 打分排序
    scored = []
    for bvid, v in all_videos.items():
        v['score'] = score_video(v)
        scored.append(v)
    scored.sort(key=lambda x: x['score'], reverse=True)

    # 5. 输出 top 50 供人工筛选
    print("\n" + "=" * 60)
    print("Top 50 候选视频（按相关度打分）")
    print("=" * 60)
    for i, v in enumerate(scored[:50]):
        print(f"{i+1:2d}. [{v['score']:5.1f}] {v['title'][:40]:40s} | {v['author'][:15]:15s} | 播放:{v['play']:>8} | 时长:{v['duration']:>6} | {v['bvid']}")

    # 6. 保存搜索清单
    search_list = {
        'keywords': KEYWORDS,
        'total_unique': len(all_videos),
        'search_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'all_videos': scored,
    }
    with open(os.path.join(OUTPUT_DIR, '相关视频搜索清单.json'), 'w', encoding='utf-8') as f:
        json.dump(search_list, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 搜索清单已保存: {os.path.join(OUTPUT_DIR, '相关视频搜索清单.json')}")

    # 7. 选定 top 25 进入抓取队列
    top_n = 25
    selected = scored[:top_n]
    print(f"\n选定 Top {top_n} 进入评论+字幕抓取")

    # 保存选定列表
    with open(os.path.join(OUTPUT_DIR, '精选视频列表.json'), 'w', encoding='utf-8') as f:
        json.dump(selected, f, ensure_ascii=False, indent=2)

    return selected

if __name__ == '__main__':
    main()
