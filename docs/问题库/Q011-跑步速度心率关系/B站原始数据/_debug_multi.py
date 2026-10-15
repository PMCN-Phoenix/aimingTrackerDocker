# -*- coding: utf-8 -*-
import sys, os, time, json, hashlib, urllib.parse
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool
import requests

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

s = requests.Session()
s.proxies = {"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
})
pool = BiliCookiePool()
s.headers["Cookie"] = pool.get_cookie()

nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=20).json()
print("login:", nav["data"].get("uname"))
wbi = nav["data"]["wbi_img"]
img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
mixin = "".join((img + sub)[i] for i in MIXIN)[:32]

def sign(p):
    p = dict(p); p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q + mixin).encode()).hexdigest()
    return p

# 测试 shortlist 里的多个视频
test = [
    ("BV1Lo4y1G7dD", "1132824018"),   # 周观云 18min
    ("BV1Vm41127RA", "1509874194"),   # 鞋吧 18min
    ("BV1zo4y1m7uN", "340983873"),    # 子章老师 5min
    ("BV1PZ421K7BL", "1653688265"),   # 柏柏湾 4min 911k
    ("BV1J2eY6SEtn", "42042066814"),  # RunnerLoc 23min
    ("BV18M41147Y7", "1040378425"),   # 容易PB VDOT 10min
    ("BV1NkoLBFEdg", "37787796461"),  # 西卡卡卡 5min
]
for bv, cid in test:
    q = sign({"bvid": bv, "cid": cid, "web_location": "333.1007"})
    d = s.get("https://api.bilibili.com/x/player/wbi/v2", params=q,
              headers={"Referer": f"https://www.bilibili.com/video/{bv}/"}, timeout=20).json()
    subs = ((d.get("data") or {}).get("subtitle") or {}).get("subtitles") or []
    ai_status = (d.get("data") or {}).get("aid")  # just checking structure
    print(f"{bv}: {len(subs)} subtitles -> {[(x.get('lan'), x.get('subtitle_url','')[:60]) for x in subs]}")
    time.sleep(1.5)
