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

# 验证登录
nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=20).json()
print("login:", nav["data"].get("uname"), "isLogin:", nav["data"].get("isLogin"))

wbi = nav["data"]["wbi_img"]
img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
mixin = "".join((img + sub)[i] for i in MIXIN)[:32]
print("mixin:", mixin)

def sign(p):
    p = dict(p)
    p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q + mixin).encode()).hexdigest()
    return p

# 测试视频 BV1Lo4y1G7dD, cid=1132824018
bvid = "BV1Lo4y1G7dD"
cid = "1132824018"
q = sign({"bvid": bvid, "cid": cid, "web_location": "333.1007"})
print("\nparams:", q)
r = s.get("https://api.bilibili.com/x/player/wbi/v2", params=q,
          headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"}, timeout=20)
print("status:", r.status_code)
d = r.json()
print("code:", d.get("code"), "msg:", d.get("message"))
# 打印 subtitle 相关字段
sub_obj = (d.get("data") or {}).get("subtitle") or {}
print("\nsubtitle object keys:", list(sub_obj.keys()))
print("subtitle:", json.dumps(sub_obj, ensure_ascii=False, indent=2)[:2000])
