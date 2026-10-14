# -*- coding: utf-8 -*-
"""
18-拉出去打不到人 Reddit 数据收集 (DDG 找帖 + Reddit RSS 取正文评论)
"""
import json, time, re, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from html import unescape
from pathlib import Path

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景\18-拉出去打不到人-Reddit原始数据")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
opener = urllib.request.build_opener(urllib.request.ProxyHandler(
    {"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}))
opener.addheaders = [("User-Agent", UA)]
NS = {"a": "http://www.w3.org/2005/Atom"}

QUERIES = [
    "reddit valorant overflick too far fix",
    "reddit valorant flick goes past enemy",
    "reddit valorant can't hit after peeking out",
    "reddit valorant miss every duel first",
    "reddit valorant shooting while moving punishment",
    "reddit valorant counter strafe tips",
    "reddit valorant nervous shaky hands aim peek",
    "reddit valorant wide swing miss",
    "reddit FPSAimTrainer overflick correction",
    "reddit valorant why do I miss easy shots",
    "reddit valorant preaim head level when swinging",
    "reddit valorant crosshair placement peek wide",
    "reddit valorant panic peek lose gunfight",
    "reddit valorant sensitivity overflick",
]

def fetch(url, timeout=40):
    with opener.open(url, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore")

def ddg_search(q):
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q)
    body = fetch(url)
    links = re.findall(r"uddg=([^&\"]+)", body)
    out = []
    for l in links:
        u = urllib.parse.unquote(l)
        m = re.search(r"reddit\.com/r/([^/]+)/comments/([a-z0-9]+)", u)
        if m:
            out.append({"sub": m.group(1), "id": m.group(2), "url": f"https://www.reddit.com/r/{m.group(1)}/comments/{m.group(2)}/"})
    return out

def clean_html(t):
    t = re.sub(r"<[^>]+>", " ", t or "")
    t = unescape(t)
    return re.sub(r"\s+", " ", t).strip()

def parse_feed(xml_text):
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return []
    out = []
    for e in root.findall("a:entry", NS):
        title = e.find("a:title", NS)
        link = e.find("a:link", NS)
        content = e.find("a:content", NS)
        author = e.find("a:author/a:name", NS)
        out.append({
            "title": title.text if title is not None else "",
            "link": link.get("href") if link is not None else "",
            "content": clean_html(content.text) if content is not None else "",
            "author": author.text if author is not None else "",
        })
    return out

def main():
    candidates = {}
    for i, q in enumerate(QUERIES, 1):
        print(f"[ddg {i}/{len(QUERIES)}] {q}")
        try:
            hits = ddg_search(q)
        except Exception as e:
            print("  err:", e)
            hits = []
        for h in hits:
            if h["id"] not in candidates:
                h["queries"] = [q]
                candidates[h["id"]] = h
                print("  +", h["url"])
            else:
                candidates[h["id"]]["queries"].append(q)
        time.sleep(6)

    print(f"\n候选帖子数: {len(candidates)}")

    posts = []
    for i, (pid, h) in enumerate(candidates.items(), 1):
        url = f"https://www.reddit.com{h['url'].replace('https://www.reddit.com','')}.rss?limit=30"
        print(f"[rss {i}/{len(candidates)}] {h['url']}")
        try:
            feed = parse_feed(fetch(url, timeout=30))
        except Exception as e:
            print("  err:", e)
            feed = []
            time.sleep(12)
            try:
                feed = parse_feed(fetch(url, timeout=30))
            except Exception as e2:
                print("  retry err:", e2)
        post = dict(h)
        if feed:
            post["title"] = feed[0]["title"]
            post["selftext"] = feed[0]["content"][:2500]
            post["comments"] = [{"author": c["author"], "body": c["content"][:2500]} for c in feed[1:]]
        posts.append(post)
        time.sleep(12)

    (OUT_DIR / "posts_with_comments_18_swing_miss.json").write_text(
        json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"DONE -> {OUT_DIR} ({len(posts)} posts)")

if __name__ == "__main__":
    main()
