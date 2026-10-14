# -*- coding: utf-8 -*-
import urllib.request, re
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
op = urllib.request.build_opener(urllib.request.ProxyHandler({"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}))
op.addheaders = [("User-Agent", UA), ("Accept-Language", "en-US,en;q=0.9")]
url = "https://www.reddit.com/r/VALORANT/comments/w051jz/why_is_everyone_afraid_to_push_sites/"
try:
    with op.open(url, timeout=30) as r:
        data = r.read().decode("utf-8", errors="ignore")
    print("OK len=", len(data))
    m = re.findall(r'"score":\s*(\d+)', data)
    print("scores found:", m[:10])
    m2 = re.findall(r'(\d[\d,]*)\s*(upvotes|points|votes)', data)
    print("votes text:", m2[:10])
except Exception as e:
    print("FAIL", type(e).__name__, str(e)[:150])
