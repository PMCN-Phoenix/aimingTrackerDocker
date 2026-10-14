# -*- coding: utf-8 -*-
"""
场景19 心态 - 已知帖子评论抓取 + DDG 补充搜索(带摘要)
通道: comments/.rss (已验证可用) + DDG html discovery
代理 7897, 间隔 20s, 429 退避 90s
"""
import urllib.request, urllib.parse, re, time, json
import xml.etree.ElementTree as ET
from html import unescape
from pathlib import Path

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-场景19原始数据\Reddit")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
opener = urllib.request.build_opener(urllib.request.ProxyHandler({
    "http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}))
opener.addheaders = [("User-Agent", UA)]

NS = {"a": "http://www.w3.org/2005/Atom"}

POSTS = [
    ("w051jz", "VALORANT"), ("j2zwht", "VALORANT"), ("sr0kvu", "VALORANT"),
    ("1dqg87b", "VALORANT"), ("oiqtt8", "VALORANT"), ("w2tfhm", "VALORANT"),
    ("xi09mp", "VALORANT"), ("13m2kqi", "VALORANT"), ("v8ou9l", "VALORANT"),
    ("qlldt7", "VALORANT"), ("yia93e", "VALORANT"), ("lw29ai", "VALORANT"),
    ("n4rg1j", "VALORANT"), ("j0f4v8", "AgentAcademy"), ("vrg8er", "AgentAcademy"),
]

DDG_QUERIES = [
    "reddit valorant fear of dying peek",
    "reddit valorant playing scared passive improve",
    "reddit summonerschool mentality tilt control mental",
    "reddit getdisciplined build habit automatic cue",
    "reddit valorant aggressive playstyle overextended confidence",
    "reddit FPSAimTrainer mental focus pressure performance",
]

def fetch(url, retries=2, timeout=30):
    for i in range(retries + 1):
        try:
            with opener.open(url, timeout=timeout) as r:
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

def main():
    # --- Phase 1: comments RSS ---
    results = []
    for i, (pid, sub) in enumerate(POSTS, 1):
        url = f"https://www.reddit.com/r/{sub}/comments/{pid}/.rss?limit=50"
        print(f"[post {i}/{len(POSTS)}] {pid} r/{sub}")
        xml_text = fetch(url)
        entry_list = []
        if xml_text:
            try:
                entry_list = parse_feed(xml_text)
            except Exception as e:
                print("    parse fail", e)
        post = entry_list[0] if entry_list else {"title": "", "content": "", "author": ""}
        comments = [{"author": e["author"], "body": e["content"][:2800]} for e in entry_list[1:]]
        results.append({
            "id": pid, "subreddit": sub,
            "url": f"https://www.reddit.com/r/{sub}/comments/{pid}/",
            "title": post["title"], "body": post["content"][:3000],
            "author": post["author"], "comments": comments,
        })
        print(f"    title: {post['title'][:70]} | comments: {len(comments)}")
        time.sleep(20)

    (OUT_DIR / "known_posts_comments.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- Phase 2: DDG 补充搜索 (带摘要) ---
    discovered = {}
    for q in DDG_QUERIES:
        url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": q})
        print(f"[ddg] {q}")
        try:
            data = fetch(url, retries=1, timeout=25)
        except Exception as e:
            print("  FAIL", e)
            data = None
        if not data:
            time.sleep(5)
            continue
        blocks = re.findall(r'(result__a.*?)(?=result__a|$)', data, re.S)
        for b in blocks[:8]:
            m = re.search(r'uddg=([^"&]+)', b)
            if not m:
                continue
            u = urllib.parse.unquote(m.group(1))
            if "reddit.com" not in u or "/comments/" not in u:
                continue
            pm = re.search(r"/comments/([a-z0-9]+)/", u)
            pid = pm.group(1) if pm else u
            tm = re.search(r'result__a"[^>]*>(.*?)</a>', b, re.S)
            title = clean_html(tm.group(1)) if tm else ""
            sm = re.search(r'result__snippet"[^>]*>(.*?)</a>|result__snippet"[^>]*>(.*?)</div>', b, re.S)
            snippet = clean_html((sm.group(1) or sm.group(2)) if sm else "")
            if pid not in discovered:
                discovered[pid] = {"title": title, "url": u, "snippet": snippet[:400]}
                print(f"  {title[:75]}")
                print(f"    {u}")
                print(f"    snippet: {snippet[:200]}")
        time.sleep(5)

    (OUT_DIR / "ddg_extra_discovered.json").write_text(
        json.dumps(discovered, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nDONE")

if __name__ == "__main__":
    main()
