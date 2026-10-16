"""
用Selenium Edge浏览器批量收集Reddit r/VALORANT残局1v1相关帖子
利用浏览器渲染绕过API反爬
"""
import json
import time
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-Reddit原始数据")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 30个关键词
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

def create_driver():
    """创建Edge浏览器实例"""
    options = Options()
    options.add_argument('--headless')  # 无头模式
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0')
    # 禁用图片加载加速
    options.add_argument('--blink-settings=imagesEnabled=false')
    
    driver = webdriver.Edge(options=options)
    driver.set_page_load_timeout(30)
    return driver

def parse_search_results(driver, keyword):
    """解析搜索结果页面，提取帖子信息"""
    posts = []
    
    # Reddit新UI的帖子选择器
    # 尝试多种选择器
    selectors = [
        'shreddit-post',  # 新UI
        'div[data-testid="post-container"]',
        'article',
        'div[class*="Post"]',
    ]
    
    post_elements = []
    for selector in selectors:
        try:
            post_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if post_elements:
                break
        except:
            continue
    
    for elem in post_elements:
        try:
            # 提取标题
            title = ''
            title_selectors = ['a[slot="title"]', 'h3', 'a[data-click-id="body"]', 'a[href*="/comments/"]']
            for ts in title_selectors:
                try:
                    title_elem = elem.find_element(By.CSS_SELECTOR, ts)
                    title = title_elem.text.strip()
                    if title:
                        break
                except:
                    continue
            
            # 提取链接
            url = ''
            try:
                link_elem = elem.find_element(By.CSS_SELECTOR, 'a[href*="/comments/"]')
                url = link_elem.get_attribute('href')
            except:
                pass
            
            # 提取票数
            score = 0
            try:
                score_elem = elem.find_element(By.CSS_SELECTOR, '[class*="voteCount"], [aria-label*="votes"], [class*="score"]')
                score_text = score_elem.text.strip()
                # 处理"1.2k"格式
                if 'k' in score_text.lower():
                    score = int(float(score_text.lower().replace('k', '')) * 1000)
                elif score_text.isdigit():
                    score = int(score_text)
            except:
                pass
            
            # 提取评论数
            comments = 0
            try:
                comment_elem = elem.find_element(By.CSS_SELECTOR, '[class*="commentCount"], a[href*="comments"] span, [aria-label*="comments"]')
                comment_text = comment_elem.text.strip()
                if 'k' in comment_text.lower():
                    comments = int(float(comment_text.lower().replace('k', '')) * 1000)
                elif comment_text.isdigit():
                    comments = int(comment_text)
            except:
                pass
            
            # 从URL提取id
            post_id = ''
            if url:
                m = re.search(r'/comments/([a-z0-9]+)/', url)
                if m:
                    post_id = m.group(1)
            
            if title and url and post_id:
                posts.append({
                    'id': post_id,
                    'title': title,
                    'url': url,
                    'score': score,
                    'num_comments': comments,
                    'keyword': keyword,
                })
        except Exception as e:
            continue
    
    return posts

def search_and_scroll(driver, keyword, max_scrolls=3):
    """搜索关键词并滚动加载更多结果"""
    all_posts = []
    seen_ids = set()
    
    # 构造搜索URL - 使用old.reddit.com更容易解析
    url = f"https://old.reddit.com/r/VALORANT/search?q={keyword.replace(' ', '+')}&sort=top&t=all&restrict_sr=on"
    
    try:
        driver.get(url)
        time.sleep(3)  # 等待页面加载
        
        for scroll in range(max_scrolls):
            # 解析当前页面
            posts = parse_old_reddit(driver, keyword)
            for p in posts:
                if p['id'] not in seen_ids:
                    seen_ids.add(p['id'])
                    all_posts.append(p)
            
            # 滚动到底部加载更多
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # 最后再解析一次
        posts = parse_old_reddit(driver, keyword)
        for p in posts:
            if p['id'] not in seen_ids:
                seen_ids.add(p['id'])
                all_posts.append(p)
    except Exception as e:
        print(f"  搜索错误: {e}")
    
    return all_posts

def parse_old_reddit(driver, keyword):
    """解析old.reddit.com搜索结果"""
    posts = []
    
    # old.reddit.com的帖子结构
    things = driver.find_elements(By.CSS_SELECTOR, 'div.thing')
    
    for thing in things:
        try:
            # 标题
            title_elem = thing.find_element(By.CSS_SELECTOR, 'a.title')
            title = title_elem.text.strip()
            url = title_elem.get_attribute('href')
            
            # 票数
            score = 0
            try:
                score_elem = thing.find_element(By.CSS_SELECTOR, 'div.score.unvoted, span.score.unvoted')
                score_text = score_elem.text.strip()
                if 'k' in score_text.lower():
                    score = int(float(score_text.lower().replace('k', '')) * 1000)
                elif score_text and score_text != '•':
                    try:
                        score = int(score_text)
                    except:
                        pass
            except:
                pass
            
            # 评论数
            comments = 0
            try:
                comment_elem = thing.find_element(By.CSS_SELECTOR, 'a.comments')
                comment_text = comment_elem.text.strip()
                m = re.search(r'(\d+)', comment_text)
                if m:
                    comments = int(m.group(1))
            except:
                pass
            
            # id
            post_id = thing.get_attribute('data-fullname')
            if post_id and '_' in post_id:
                post_id = post_id.split('_')[1]
            
            if title and url and post_id:
                posts.append({
                    'id': post_id,
                    'title': title,
                    'url': url,
                    'score': score,
                    'num_comments': comments,
                    'keyword': keyword,
                })
        except:
            continue
    
    return posts

def main():
    print("启动Edge浏览器...")
    driver = create_driver()
    
    all_posts = {}
    keyword_stats = {}
    
    try:
        for i, kw in enumerate(KEYWORDS, 1):
            print(f"[{i}/{len(KEYWORDS)}] 搜索: {kw}")
            posts = search_and_scroll(driver, kw, max_scrolls=2)
            keyword_stats[kw] = len(posts)
            new_count = 0
            for p in posts:
                if p['id'] not in all_posts:
                    all_posts[p['id']] = p
                    new_count += 1
            print(f"  获取 {len(posts)} 条，新增 {new_count} 条，累计 {len(all_posts)} 条")
            time.sleep(2)
    finally:
        driver.quit()
    
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
        f.write(f"> 收集方式：Selenium Edge浏览器 + old.reddit.com\n")
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
