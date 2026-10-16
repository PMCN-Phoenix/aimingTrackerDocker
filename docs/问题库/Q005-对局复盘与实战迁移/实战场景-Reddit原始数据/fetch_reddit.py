"""
批量收集Reddit r/VALORANT残局1v1相关帖子
使用Reddit公开JSON API
"""
import requests
import json
import time
from pathlib import Path

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-Reddit原始数据")
OUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

PROXIES = {
    'http': 'http://127.0.0.1:7892',
    'https': 'http://127.0.0.1:7892',
}

# 20个关键词，覆盖残局1v1箱体的各个角度
KEYWORDS = [
    "1v1 clutch valorant",
    "post plant 1v1 valorant",
    "clutch situation valorant tips",
    "how to win 1v1 valorant",
    "retake 1v1 valorant",
    "jiggle peek valorant",
    "wide swing valorant",
    "peeking tips valorant",
    "1v1 post plant positioning",
    "clutch mentality valorant",
    "how to peek someone holding angle",
    "post plant aggressive angles",
    "1v2 clutch valorant",
    "valorant holding angle",
    "crosshair placement valorant",
    "movement valorant peek",
    "crouch peek valorant",
    "jump peek valorant",
    "valorant 1v1 tips",
    "clutch guide valorant",
]

def search_reddit(keyword, sort="top", t="all", limit=100):
    """搜索Reddit帖子（使用old.reddit.com，反爬更宽松）"""
    url = f"https://old.reddit.com/r/VALORANT/search.json"
    params = {
        'q': keyword,
        'sort': sort,
        't': t,
        'limit': limit,
        'restrict_sr': 'on'
    }
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=30, proxies=PROXIES)
        if r.status_code != 200:
            print(f"  状态码 {r.status_code}，等待重试...")
            time.sleep(5)
            r = requests.get(url, headers=HEADERS, params=params, timeout=30, proxies=PROXIES)
        if r.status_code != 200:
            print(f"  重试后仍为 {r.status_code}")
            return []
        data = r.json()
        posts = []
        for child in data.get('data', {}).get('children', []):
            p = child['data']
            posts.append({
                'id': p['id'],
                'title': p['title'],
                'score': p['score'],
                'num_comments': p['num_comments'],
                'url': f"https://www.reddit.com{p['permalink']}",
                'selftext': p.get('selftext', '')[:500],  # 只取前500字符
                'author': p.get('author', ''),
                'created_utc': p.get('created_utc', 0),
                'link_flair_text': p.get('link_flair_text', ''),
                'upvote_ratio': p.get('upvote_ratio', 0),
                'keyword': keyword,
            })
        return posts
    except Exception as e:
        print(f"  错误: {e}")
        return []

def main():
    all_posts = {}
    keyword_stats = {}
    
    for i, kw in enumerate(KEYWORDS, 1):
        print(f"[{i}/{len(KEYWORDS)}] 搜索: {kw}")
        posts = search_reddit(kw)
        keyword_stats[kw] = len(posts)
        new_count = 0
        for p in posts:
            if p['id'] not in all_posts:
                all_posts[p['id']] = p
                new_count += 1
        print(f"  获取 {len(posts)} 条，新增 {new_count} 条，累计 {len(all_posts)} 条")
        time.sleep(2)  # 限速
    
    # 按分数排序
    sorted_posts = sorted(all_posts.values(), key=lambda x: x['score'], reverse=True)
    
    # 保存完整数据
    full_file = OUT_DIR / "reddit_posts_full.json"
    full_file.write_text(json.dumps(sorted_posts, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n完整数据已保存: {full_file} ({len(sorted_posts)} 条)")
    
    # 保存Markdown索引
    md_file = OUT_DIR / "reddit_posts_index.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# Reddit r/VALORANT 残局1v1相关帖子索引\n\n")
        f.write(f"> 收集时间：2026-10-12\n")
        f.write(f"> 关键词数量：{len(KEYWORDS)}个\n")
        f.write(f"> 去重后总帖子数：{len(sorted_posts)}\n\n")
        
        f.write("## 关键词统计\n\n")
        f.write("| 关键词 | 获取数 |\n|---|---|\n")
        for kw, count in keyword_stats.items():
            f.write(f"| {kw} | {count} |\n")
        
        f.write(f"\n## 全部帖子（按票数降序，共{len(sorted_posts)}条）\n\n")
        f.write("| # | 票数 | 评论 | 标题 | 关键词 |\n")
        f.write("|---|---|---|---|---|\n")
        for i, p in enumerate(sorted_posts, 1):
            title = p['title'].replace('|', '\\|')[:80]
            f.write(f"| {i} | {p['score']} | {p['num_comments']} | [{title}]({p['url']}) | {p['keyword']} |\n")
    
    print(f"Markdown索引已保存: {md_file}")
    
    # 输出Top 30
    print(f"\n=== Top 30 帖子 ===")
    for i, p in enumerate(sorted_posts[:30], 1):
        print(f"{i:2d}. [{p['score']:5d}票/{p['num_comments']:3d}评] {p['title'][:70]}")

if __name__ == "__main__":
    main()
