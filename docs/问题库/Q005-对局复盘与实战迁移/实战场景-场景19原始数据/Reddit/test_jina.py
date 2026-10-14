# -*- coding: utf-8 -*-
"""测试 r.jina.ai reader 代理读 reddit 帖子页(markdown, 含票数)"""
import urllib.request
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"
op = urllib.request.build_opener(urllib.request.ProxyHandler({"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}))
op.addheaders = [("User-Agent", UA)]
target = "https://www.reddit.com/r/VALORANT/comments/w051jz/why_is_everyone_afraid_to_push_sites/"
url = "https://r.jina.ai/" + target
try:
    with op.open(url, timeout=40) as r:
        data = r.read().decode("utf-8", errors="ignore")
    print("OK len=", len(data))
    print(data[:2000])
except Exception as e:
    print("FAIL", type(e).__name__, str(e)[:150])
