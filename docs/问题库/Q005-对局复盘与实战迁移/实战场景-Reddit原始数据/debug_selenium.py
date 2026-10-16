"""调试Selenium加载Reddit页面"""
from selenium import webdriver
from selenium.webdriver.edge.options import Options
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1920,1080')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0')

driver = webdriver.Edge(options=options)
driver.set_page_load_timeout(30)

try:
    url = "https://old.reddit.com/r/VALORANT/search?q=1v1+clutch+valorant&sort=top&t=all&restrict_sr=on"
    print(f"加载: {url}")
    driver.get(url)
    time.sleep(5)
    
    print(f"当前URL: {driver.current_url}")
    print(f"页面标题: {driver.title}")
    
    # 保存页面HTML
    html = driver.page_source
    with open(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-Reddit原始数据\debug_page.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML长度: {len(html)}")
    print(f"HTML前2000字符:\n{html[:2000]}")
    
    # 检查是否有帖子元素
    things = driver.find_elements("css selector", "div.thing")
    print(f"\ndiv.thing 数量: {len(things)}")
    
    # 检查其他可能的元素
    for sel in ['shreddit-post', 'article', 'div[data-testid="post-container"]', 'a[href*="/comments/"]']:
        elems = driver.find_elements("css selector", sel)
        print(f"{sel} 数量: {len(elems)}")
        
finally:
    driver.quit()
