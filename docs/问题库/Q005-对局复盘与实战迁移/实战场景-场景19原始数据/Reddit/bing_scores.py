# -*- coding: utf-8 -*-
"""Bing 搜索补票数: 用帖子标题搜, 从摘要里提取 votes/分数字样"""
import urllib.request, urllib.parse, re, time

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
opener = urllib.request.build_opener(urllib.request.ProxyHandler({
    "http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}))
opener.addheaders = [("User-Agent", UA)]

POSTS = [
    ("w051jz", "Why is Everyone Afraid to Push Sites"),
    ("sr0kvu", "Peek Anxiety valorant"),
    ("1dqg87b", "how do i get rid of ranked anxiety valorant"),
    ("oiqtt8", "How to overcome lack of confidence valorant"),
    ("w2tfhm", "any tips on how to gain more confidence valorant"),
    ("xi09mp", "How to stop tilt valorant"),
    ("13m2kqi", "how to have fun not tilt at valorant"),
    ("v8ou9l", "The Mindset that will help you improve valorant"),
    ("qlldt7", "how to maintain healthy mental valorant"),
    ("yia93e", "tips to getting out of a bad mentality valorant"),
    ("lw29ai", "My hands shake a ton any tips valorant"),
    ("n4rg1j", "how do i fix my nervousness and shaky aim valorant"),
    ("j0f4v8", "Im always scared to push in while playing raze"),
]

for pid, q in POSTS:
    url = "https://www.bing.com/search?" + urllib.parse.urlencode({"q": q, "count": 10})
    try:
        with opener.open(url, timeout=25) as r:
            data = r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(pid, "FAIL", type(e).__name__, str(e)[:80])
        time.sleep(3)
        continue
    # find snippet blocks mentioning reddit and votes
    blocks = re.findall(r'<li class="b_algo".*?</li>', data, re.S)
    found = []
    for b in blocks:
        if "reddit" in b.lower():
            txt = re.sub(r"<[^>]+>", " ", b)
            txt = re.sub(r"\s+", " ", txt)
            m = re.search(r"([\d.,]+[kKmM]?)\s*(votes|points|upvotes)", txt, re.I)
            if m:
                found.append(m.group(0))
    print(pid, "->", found if found else "(no vote info in snippets)")
    time.sleep(3)
