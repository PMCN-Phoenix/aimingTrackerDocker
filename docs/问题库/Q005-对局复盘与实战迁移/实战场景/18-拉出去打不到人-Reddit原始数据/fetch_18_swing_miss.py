# -*- coding: utf-8 -*-
"""
18-拉出去打不到人 Reddit 数据收集
方法: www.reddit.com search.rss 搜索 + comments via {permalink}.rss (urllib, 代理 7897)
注意: RSS 不提供票数, 以标题/内容相关性人工排序, 并补充抓取 post .json 尝试拿 score
"""
import json, time, re
import urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from html import unescape
from pathlib import Path

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景\18-拉出去打不到人-Reddit原始数据")
OUT_DIR.mkdir(parents=True, exist_ok=True)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
PROXY = "http://127.0.0.1:7897"
opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))
opener.addheaders = [("User-Agent", UA)]

NS = {"a": "http://www.w3.org/2005/Atom"}

SUBS = ["VALORANT", "FPSAimTrainer"]

KEYWORDS = [
    "can't hit after peeking",
    "miss every shot when peeking",
    "overflick",
    "micro adjustment after peek",
    "shooting while moving",
    "counter strafe timing",
    "nervous shaky hands duel",
    "why do i miss every duel",
]

def fetch(url, retries=4):
    for i in range(retries + 1):
        try:
            with opener.open(url, timeout=40) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            wait = 15 if "429" in str(e) else 6
            print(f"    retry{i}: {e} -> wait {wait}s")
            time.sleep(wait)
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
        link = e.find("a:link", NS)
        content = e.find("a:content", NS)
        author = e.find("a:author/a:name", NS)
        eid = e.find("a:id", NS)
        out.append({
            "title": title.text if title is not None else "",
            "link": link.get("href") if link is not None else "",
            "content": clean_html(content.text) if content is not None else "",
            "author": author.text if author is not None else "",
            "id": eid.text if eid is not None else "",
        })
    return out

def main():
    stats = {}
    all_posts = {}
    for sub in SUBS:
        for kw in KEYWORDS:
            q = urllib.parse.urlencode({"q": kw, "sort": "top", "t": "all", "limit": 25, "restrict_sr": "on"})
            url = f"https://www.reddit.com/r/{sub}/search.rss?{q}"
            print(f"[search] {sub} :: {kw}")
            xml_text = fetch(url)
            if not xml_text:
                stats[f"{sub}::{kw}"] = 0
                continue
            entries = parse_feed(xml_text)
            stats[f"{sub}::{kw}"] = len(entries)
            for en in entries:
                m = re.search(r"/comments/([a-z0-9]+)/", en["id"] + en["link"])
                if not m:
                    continue
                pid = m.group(1)
                if pid in all_posts:
                    continue
                all_posts[pid] = {
                    "id": pid, "subreddit": sub,
                    "title": en["title"], "url": en["link"],
                    "selftext": en["content"][:2000], "author": en["author"],
                    "matched_keywords": [kw],
                }
            time.sleep(8)

    posts = sorted(all_posts.values(), key=lambda x: -len(x["matched_keywords"]))
    print(f"\n去重帖子总数: {len(posts)}")
    for p in posts[:40]:
        print(f"  {len(p['matched_keywords'])}kw r/{p['subreddit']} {p['title'][:75]}")

    (OUT_DIR / "search_results_raw.json").write_text(
        json.dumps({"stats": stats, "posts": posts}, ensure_ascii=False, indent=2), encoding="utf-8")

    # 拉前30帖的评论RSS
    picked = posts[:15]
    for i, p in enumerate(picked, 1):
        permalink = f"/r/{p['subreddit']}/comments/{p['id']}/"
        url = f"https://www.reddit.com{permalink}.rss?limit=30"
        print(f"[comments {i}/{len(picked)}] {p['title'][:60]}")
        xml_text = fetch(url)
        comments = []
        if xml_text:
            entries = parse_feed(xml_text)
            # 第一条是post本身, 其余是评论
            for en in entries[1:]:
                comments.append({"author": en["author"], "body": en["content"][:2500]})
        p["comments"] = comments
        time.sleep(8)

    (OUT_DIR / "posts_with_comments_18_swing_miss.json").write_text(
        json.dumps(picked, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDONE -> {OUT_DIR}")

if __name__ == "__main__":
    main()
