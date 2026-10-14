# -*- coding: utf-8 -*-
"""测试 redlib/libreddit 镜像站读取帖子票数"""
import urllib.request, re
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
proxies = {"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}
op = urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
op.addheaders = [("User-Agent", UA)]

INSTANCES = [
    "https://redlib.catsarch.com",
    "https://redlib.perennialte.ch",
    "https://safereddit.com",
    "https://r.opnxng.com",
    "https://redlib.privacyredirect.com",
]
path = "/r/VALORANT/comments/w051jz/why_is_everyone_afraid_to_push_sites/"
for base in INSTANCES:
    url = base + path
    try:
        with op.open(url, timeout=20) as r:
            data = r.read().decode("utf-8", errors="ignore")
        scores = re.findall(r'(\d[\d.]*k?)\s*(?:points|upvotes|↑)', data)
        print(base, "OK len=", len(data), "score-ish:", scores[:5])
    except Exception as e:
        print(base, "FAIL", type(e).__name__, str(e)[:80])
