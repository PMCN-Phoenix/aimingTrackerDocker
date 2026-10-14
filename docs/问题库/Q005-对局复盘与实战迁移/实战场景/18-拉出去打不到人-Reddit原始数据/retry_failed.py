# -*- coding: utf-8 -*-
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

FAILED = [
    ("VALORANT", "kkey5d"),
    ("VALORANT", "i1woyn"),
    ("VALORANT", "14kae1n"),
    ("VALORANT", "1d0on3v"),
    ("VALORANT", "uerxp5"),
    ("VALORANT", "kit0u9"),
    ("VALORANT", "g0l792"),
    ("VALORANT", "wmhhjn"),
    ("VALORANT", "vapbch"),
    ("aimlab", "vapgic"),
]

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
        content = e.find("a:content", NS)
        author = e.find("a:author/a:name", NS)
        out.append({
            "title": title.text if title is not None else "",
            "content": clean_html(content.text) if content is not None else "",
            "author": author.text if author is not None else "",
        })
    return out

def fetch_once(url):
    with opener.open(url, timeout=30) as r:
        return r.read().decode("utf-8", errors="ignore")

existing = json.load(open(OUT_DIR / "posts_with_comments_18_swing_miss.json", encoding="utf-8"))

for sub, pid in FAILED:
    url = f"https://www.reddit.com/r/{sub}/comments/{pid}/.rss?limit=30"
    ok = False
    for attempt in range(3):
        try:
            feed = parse_feed(fetch_once(url))
            ok = True
            break
        except Exception as e:
            print(f"{pid} attempt{attempt}: {e}")
            time.sleep(20)
    if ok and feed:
        existing.append({
            "id": pid, "subreddit": sub,
            "url": f"https://www.reddit.com/r/{sub}/comments/{pid}/",
            "title": feed[0]["title"],
            "selftext": feed[0]["content"][:2500],
            "comments": [{"author": c["author"], "body": c["content"][:2500]} for c in feed[1:]],
            "queries": ["retry"],
        })
        print(f"{pid} OK title={feed[0]['title'][:60]} comments={len(feed)-1}")
    else:
        print(f"{pid} FAILED")
    time.sleep(20)

(OUT_DIR / "posts_with_comments_18_swing_miss.json").write_text(
    json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
print("DONE")
