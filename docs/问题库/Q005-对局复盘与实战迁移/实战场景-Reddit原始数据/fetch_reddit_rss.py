"""
批量收集Reddit r/VALORANT残局1v1相关帖子
使用Reddit RSS feed（无反爬限制）
"""
import requests
import json
import time
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from html import unescape

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-Reddit原始数据")
OUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

PROXIES = {
    'http': 'http://127.0.0.1:7892',
    'https': 'http://127.0.0.1:7892',
}

# 30个关键词，覆盖残局1v1箱体的各个角度
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
    "valorant 1v1 advice",
    "how to get better at clutching valorant",
    "post plant defense valorant",
    "spike defuse 1v1 valorant",
    "valorant clutch mistakes",
    "valorant 1v1 strategy",
    "how to play 1v1 valorant",
    "valorant peek technique",
    "valorant 1v1 positioning",
    "clutch round valorant",
]

def clean_html(text):
    """清理HTML标签"""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def search_reddit_rss(keyword, sort="top", t="all", limit=100):
    """通过RSS feed搜索Reddit帖子"""
    url = f"https://www.reddit.com/r/VALORANT/search.rss"
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
            print(f"  状态码 {r.status_code}")
            return []
        
        # 解析Atom XML
        root = ET.fromstring(r.text)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        posts = []
        for entry in root.findall('atom:entry', ns):
            title_elem = entry.find('atom:title', ns)
            link_elem = entry.find('atom:link', ns)
            content_elem = entry.find('atom:content', ns)
            author_elem = entry.find('atom:author/atom:name', ns)
            updated_elem = entry.find('atom:updated', ns)
            id_elem = entry.find('atom:id', ns)
            
            title = title_elem.text if title_elem is not None else ''
            link = link_elem.get('href') if link_elem is not None else ''
            content = clean_html(content_elem.text) if content_elem is not None and content_elem.text else ''
            author = author_elem.text if author_elem is not None else ''
            updated = updated_elem.text if updated_elem is not None else ''
            
            # 从id中提取帖子id
            post_id = ''
            if id_elem is not None and id_elem.text:
                m = re.search(r'/comments/([a-z0-9]+)/', id_elem.text)
                if m:
                    post_id = m.group(1)
            
            # 过滤掉非帖子（如subreddit推荐）
            if not post_id or '/r/' in link and '/comments/' not in link:
                continue
            
            posts.append({
                'id': post_id,
                'title': title,
                'url': link,
                'content': content[:500],
                'author': author,
                'updated': updated,
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
        posts = search_reddit_rss(kw)
        keyword_stats[kw] = len(posts)
        new_count = 0
        for p in posts:
            if p['id'] not in all_posts:
                all_posts[p['id']] = p
                new_count += 1
        print(f"  获取 {len(posts)} 条，新增 {new_count} 条，累计 {len(all_posts)} 条")
        time.sleep(1.5)  # 限速
    
    # 保存完整数据
    sorted_posts = list(all_posts.values())
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
        
        f.write(f"\n## 全部帖子（共{len(sorted_posts)}条）\n\n")
        f.write("| # | 标题 | 作者 | 关键词 |\n")
        f.write("|---|---|---|---|\n")
        for i, p in enumerate(sorted_posts, 1):
            title = p['title'].replace('|', '\\|')[:80]
            f.write(f"| {i} | [{title}]({p['url']}) | {p['author']} | {p['keyword']} |\n")
    
    print(f"Markdown索引已保存: {md_file}")
    
    # 输出前30条
    print(f"\n=== 前30条帖子 ===")
    for i, p in enumerate(sorted_posts[:30], 1):
        print(f"{i:2d}. {p['title'][:70]}")

if __name__ == "__main__":
    main()
