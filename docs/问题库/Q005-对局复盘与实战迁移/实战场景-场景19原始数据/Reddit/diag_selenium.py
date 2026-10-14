# -*- coding: utf-8 -*-
"""诊断: headless Edge 打开 www.reddit.com 帖子页, 存截图+源码看渲染了什么"""
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options

options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1200")
options.add_argument("--proxy-server=http://127.0.0.1:7897")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Edge(options=options)
driver.set_page_load_timeout(40)
url = "https://www.reddit.com/r/VALORANT/comments/w051jz/why_is_everyone_afraid_to_push_sites/"
driver.get(url)
time.sleep(8)
print("title:", driver.title)
print("url:", driver.current_url)
src = driver.page_source
print("src len:", len(src))
with open(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-场景19原始数据\Reddit\diag_page.html", "w", encoding="utf-8") as f:
    f.write(src)
driver.save_screenshot(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-场景19原始数据\Reddit\diag_shot.png")
driver.quit()
print("DONE")
