# -*- coding: utf-8 -*-
"""场景19 第二轮: DDG 新发现帖子的评论 RSS 抓取"""
import urllib.request, re, time, json
import xml.etree.ElementTree as ET
from html import unescape
from pathlib import Path

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-场景19原始数据\Reddit")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}))
opener.addheaders = [("User-Agent", UA)]
NS = {"a": "http://www.w3.org/2005/Atom"}

POSTS = [
    ("vkg9ip", "AgentAcademy"),
    ("1brbcl8", "VALORANT"),
    ("wrn2oi", "VALORANT"),
    ("1d3ymev", "VALORANT"),
    ("xr7kgp", "VALORANT"),
    ("f8ehv1", "FPSAimTrainer"),
    ("1cwy4b1", "FPSAimTrainer"),
    ("57qrwp", "summonerschool"),
    ("2jvg7m", "summonerschool"),
    ("9baeyd", "summonerschool"),
    ("197doy3", "getdisciplined"),
]

def fetch(url, retries=2):
    for i in range(retries + 1):
        try:
            with opener.open(url, timeout=40) as r:
                return r.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("    429, sleep 90s")
                time.sleep(90)
            else:
                print(f"    HTTP {e.code}")
                time.sleep(10)
        except Exception as e:
            print(f"    retry{i}: {type(e).__name__} {str(e)[:90]}")
            time.sleep(12)
    return None

def clean_html(t):
    t = re.sub(r"<[^>]+>", " ", t or "")
    t = unescape(t)
    return re.sub(r"\s+", " ", t).strip()

def parse_feed(xml_text):
    root = ET.fromstring(xml_text)
    out = []
    for e in root.findall("a:entry", NS):
        title = e.find("a:title", NS)
        content = e.find("a:content", NS)
        author = e.find("a:author/a:name", NS)
        out.append({
            "title": (title.text or "") if title is not None else "",
            "content": clean_html(content.text) if content is not None else "",
            "author": author.text if author is not None else "",
        })
    return out

results = []
for i, (pid, sub) in enumerate(POSTS, 1):
    url = f"https://www.reddit.com/r/{sub}/comments/{pid}/.rss?limit=50"
    print(f"[post {i}/{len(POSTS)}] {pid} r/{sub}")
    xml_text = fetch(url)
    entries = []
    if xml_text:
        try:
            entries = parse_feed(xml_text)
        except Exception as e:
            print("    parse fail", e)
    post = entries[0] if entries else {"title": "", "content": "", "author": ""}
    comments = [{"author": e["author"], "body": e["content"][:2800]} for e in entries[1:]]
    results.append({
        "id": pid, "subreddit": sub,
        "url": f"https://www.reddit.com/r/{sub}/comments/{pid}/",
        "title": post["title"], "body": post["content"][:3000],
        "author": post["author"], "comments": comments,
    })
    print(f"    title: {post['title'][:70]} | comments: {len(comments)}")
    time.sleep(20)

(OUT_DIR / "round2_posts_comments.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print("DONE")
