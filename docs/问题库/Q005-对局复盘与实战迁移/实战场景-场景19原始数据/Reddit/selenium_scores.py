# -*- coding: utf-8 -*-
"""Selenium 无头 Edge 读 old.reddit.com 帖子页: 拿票数+正文+高赞评论"""
import json, time, re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-场景19原始数据\Reddit")

POSTS = [
    ("w051jz", "VALORANT", "Why is Everyone Afraid to Push Sites"),
    ("j2zwht", "VALORANT", "people too scared to rush site"),
    ("sr0kvu", "VALORANT", "Peek Anxiety"),
    ("1dqg87b", "VALORANT", "how do i get rid of ranked anxiety"),
    ("oiqtt8", "VALORANT", "How to overcome lack of confidence"),
    ("w2tfhm", "VALORANT", "any tips on how to gain more confidence"),
    ("xi09mp", "VALORANT", "How to stop tilt"),
    ("13m2kqi", "VALORANT", "how to have fun not tilt at valorant"),
    ("v8ou9l", "VALORANT", "The Mindset that will help you improve"),
    ("qlldt7", "VALORANT", "how to maintain healthy mental"),
    ("yia93e", "VALORANT", "tips to getting out of a bad mentality"),
    ("lw29ai", "VALORANT", "My hands shake a ton any tips"),
    ("n4rg1j", "VALORANT", "how do i fix my nervousness and shaky aim"),
    ("j0f4v8", "AgentAcademy", "Im always scared to push in while playing raze"),
    ("vrg8er", "AgentAcademy", "what do i do when my teammates keep pushing"),
]

options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1200")
options.add_argument("--proxy-server=http://127.0.0.1:7897")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Edge(options=options)
driver.set_page_load_timeout(40)

results = []
for pid, sub, slug in POSTS:
    url = f"https://old.reddit.com/r/{sub}/comments/{pid}/"
    print(f"[open] {pid} {sub}")
    rec = {"id": pid, "subreddit": sub, "url": url, "score": None, "title": "", "body": "", "comments": []}
    try:
        driver.get(url)
        time.sleep(4)
        # score
        for sel in ['span.score.unvoted', 'span.score.likes', 'span.score.dislikes', 'div.score.unvoted']:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                t = el.text.strip()
                if t and t != "•":
                    rec["score_text"] = t
                    break
            except Exception:
                pass
        # title
        try:
            rec["title"] = driver.find_element(By.CSS_SELECTOR, 'a.title').text.strip()
        except Exception:
            try:
                rec["title"] = driver.find_element(By.CSS_SELECTOR, 'p.title a.title').text.strip()
            except Exception:
                pass
        # body
        try:
            rec["body"] = driver.find_element(By.CSS_SELECTOR, 'div.usertext-body').text[:2500]
        except Exception:
            pass
        # comments
        try:
            comment_els = driver.find_elements(By.CSS_SELECTOR, 'div.comment div.usertext-body')
            scores = driver.find_elements(By.CSS_SELECTOR, 'div.comment span.score.unvoted')
            for i, ce in enumerate(comment_els[:12]):
                st = scores[i].text.strip() if i < len(scores) else ""
                rec["comments"].append({"score_text": st, "body": ce.text[:1800]})
        except Exception:
            pass
    except Exception as e:
        rec["error"] = f"{type(e).__name__} {str(e)[:100]}"
    print(f"    score={rec.get('score_text','?')} title={rec['title'][:60]} cmts={len(rec['comments'])}")
    results.append(rec)
    time.sleep(3)

driver.quit()
(OUT_DIR / "selenium_posts.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print("DONE")
