# -*- coding: utf-8 -*-
import urllib.request, re
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
op = urllib.request.build_opener(urllib.request.ProxyHandler({"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}))
op.addheaders = [("User-Agent", UA)]
url = "https://redlib.privacyredirect.com/r/VALORANT/comments/w051jz/why_is_everyone_afraid_to_push_sites/"
with op.open(url, timeout=25) as r:
    data = r.read().decode("utf-8", errors="ignore")
# strip tags, show readable text around vote elements
txt = re.sub(r"<script.*?</script>", " ", data, flags=re.S)
txt = re.sub(r"<style.*?</style>", " ", txt, flags=re.S)
txt = re.sub(r"<[^>]+>", "\n", txt)
lines = [l.strip() for l in txt.split("\n") if l.strip()]
print("\n".join(lines[:80]))
