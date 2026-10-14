# -*- coding: utf-8 -*-
"""
场景19 前压心态与习惯化 - Reddit RSS 抓取
通道: www.reddit.com search.rss (restrict_sr=on, sort=top, t=all) + 评论 .rss
代理: 127.0.0.1:7897  (7892 未监听; .json 端点 403 已验证, RSS 无 score 字段)
限速: 每次请求间隔 6s, 429 退避 20s 重试
"""
import json, time, re
import urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from html import unescape
from pathlib import Path

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-场景19原始数据\Reddit")
OUT_DIR.mkdir(parents=True, exist_ok=True)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
PROXY = "http://127.0.0.1:7897"
opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))
opener.addheaders = [("User-Agent", UA)]

NS = {"a": "http://www.w3.org/2005/Atom"}

JOBS = [
    ("VALORANT", [
        "scared to push",
        "fear of peeking",
        "nervous when peeking",
        "anxiety gunfight",
        "stay calm under pressure",
        "playing aggressive mentality",
        "fear of dying",
        "how to stop tilting",
        "mental game tips",
        "freeze up duel",
        "can't peek aggressive",
        "clutch mentality",
    ]),
    ("AgentAcademy", [
        "scared to push",
        "anxiety when peeking",
        "calm under pressure",
        "mental game",
        "fear of dying duel",
    ]),
    ("summonerschool", [
        "how to stay calm under pressure",
        "tilt control mentality",
        "mental game improvement",
    ]),
    ("getdisciplined", [
        "how to build habits that stick",
        "make habit automatic",
    ]),
    ("FPSAimTrainer", [
        "mental game focus under pressure",
        "nervous shaky hands aim",
    ]),
]

def fetch(url, retries=2):
    for i in range(retries + 1):
        try:
            with opener.open(url, timeout=40) as r:
                return r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 90
                print(f"    429 rate-limited, sleep {wait}s")
                time.sleep(wait)
            else:
                print(f"    HTTP {e.code}")
                time.sleep(10)
        except Exception as e:
            print(f"    retry{i}: {type(e).__name__} {str(e)[:100]}")
            time.sleep(15)
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
            "title": (title.text or "") if title is not None else "",
            "link": link.get("href") if link is not None else "",
            "content": clean_html(content.text) if content is not None else "",
            "author": author.text if author is not None else "",
            "id": eid.text if eid is not None else "",
        })
    return out

def main():
    stats = {}
    all_posts = {}
    for sub, kws in JOBS:
        for kw in kws:
            q = urllib.parse.urlencode({"q": kw, "sort": "top", "t": "all", "limit": 25, "restrict_sr": "on"})
            url = f"https://www.reddit.com/r/{sub}/search.rss?{q}"
            print(f"[search] r/{sub} :: {kw}")
            xml_text = fetch(url)
            n = 0
            if xml_text:
                entries = parse_feed(xml_text)
                n = len(entries)
                for en in entries:
                    m = re.search(r"/comments/([a-z0-9]+)/", en["id"] + " " + en["link"])
                    if not m:
                        continue
                    pid = m.group(1)
                    if pid in all_posts:
                        all_posts[pid]["matched_keywords"].append(f"{sub}::{kw}")
                        continue
                    all_posts[pid] = {
                        "id": pid, "subreddit": sub,
                        "title": en["title"], "url": en["link"],
                        "selftext": en["content"][:2500], "author": en["author"],
                        "matched_keywords": [f"{sub}::{kw}"],
                    }
            stats[f"{sub}::{kw}"] = n
            print(f"    -> {n} entries")
            time.sleep(25)

    posts = sorted(all_posts.values(), key=lambda x: -len(x["matched_keywords"]))
    print(f"\n去重帖子总数: {len(posts)}")
    for p in posts[:40]:
        print(f"  {len(p['matched_keywords'])}kw r/{p['subreddit']} {p['title'][:80]}")

    (OUT_DIR / "search_results_raw.json").write_text(
        json.dumps({"stats": stats, "posts": posts}, ensure_ascii=False, indent=2), encoding="utf-8")

    # 抓前20帖的评论RSS
    picked = posts[:20]
    for i, p in enumerate(picked, 1):
        url = f"https://www.reddit.com/r/{p['subreddit']}/comments/{p['id']}/.rss?limit=40"
        print(f"[comments {i}/{len(picked)}] {p['title'][:60]}")
        xml_text = fetch(url)
        comments = []
        if xml_text:
            entries = parse_feed(xml_text)
            for en in entries[1:]:
                comments.append({"author": en["author"], "body": en["content"][:3000]})
        p["comments"] = comments
        print(f"    -> {len(comments)} comments")
        time.sleep(20)

    (OUT_DIR / "posts_with_comments_场景19_心态.json").write_text(
        json.dumps(picked, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "fetch_stats.txt").write_text(
        "场景19 Reddit RSS 抓取统计\n\n关键词命中数:\n" +
        "\n".join(f"  {k}: {v}" for k, v in stats.items()) +
        f"\n\n去重帖子总数: {len(posts)}\n抓评论帖数: {len(picked)}\n",
        encoding="utf-8")
    print(f"\nDONE -> {OUT_DIR}")

if __name__ == "__main__":
    main()
