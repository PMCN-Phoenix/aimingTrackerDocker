# -*- coding: utf-8 -*-
"""DuckDuckGo HTML 搜索发现 reddit 帖子链接（绕过 reddit search.rss 限流）"""
import urllib.request, urllib.parse, re, time, html

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
opener = urllib.request.build_opener(urllib.request.ProxyHandler({
    "http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}))
opener.addheaders = [("User-Agent", UA)]

QUERIES = [
    "reddit valorant scared to push site",
    "reddit valorant fear of peeking anxiety",
    "reddit valorant stay calm gunfight pressure",
    "reddit valorant aggressive mentality confidence",
    "reddit r/VALORANT stop tilting advice",
    "reddit valorant mental game mindset tips",
    "reddit valorant nervous shaky hands duel",
    "reddit AgentAcademy fear pushing",
]

def ddg(q):
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": q})
    with opener.open(url, timeout=30) as r:
        data = r.read().decode("utf-8", errors="ignore")
    # result links
    links = re.findall(r'uddg=([^"&]+)', data)
    titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', data, re.S)
    out = []
    for i, l in enumerate(links[:10]):
        u = urllib.parse.unquote(l)
        t = re.sub(r"<[^>]+>", "", titles[i]).strip() if i < len(titles) else ""
        out.append((t, u))
    return out

seen = {}
for q in QUERIES:
    print("###", q)
    try:
        for t, u in ddg(q):
            if "reddit.com" in u and "/comments/" in u:
                m = re.search(r"/comments/([a-z0-9]+)/", u)
                pid = m.group(1) if m else u
                if pid in seen:
                    continue
                seen[pid] = (html.unescape(t), u)
                print(f"  {html.unescape(t)[:80]}")
                print(f"    {u}")
    except Exception as e:
        print("  FAIL", type(e).__name__, str(e)[:100])
    time.sleep(4)

print("\nTOTAL reddit posts:", len(seen))
