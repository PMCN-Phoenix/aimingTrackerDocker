# -*- coding: utf-8 -*-
import urllib.request, re, urllib.parse, time

opener = urllib.request.build_opener(urllib.request.ProxyHandler(
    {'http': 'http://127.0.0.1:7897', 'https': 'http://127.0.0.1:7897'}))
opener.addheaders = [('User-Agent',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')]

queries = [
    "reddit valorant overflick fix",
    "reddit valorant can't hit after peeking",
    "reddit valorant shooting while moving counter strafe",
]
for q in queries:
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q)
    try:
        r = opener.open(url, timeout=30)
        body = r.read().decode("utf-8", errors="ignore")
        print("OK", q, len(body))
        links = re.findall(r"uddg=([^&\"]+)", body)
        seen = set()
        for l in links:
            u = urllib.parse.unquote(l)
            if "reddit.com" in u and u not in seen:
                seen.add(u)
                print("  ", u[:110])
    except Exception as e:
        print("ERR", q, e)
    time.sleep(5)
