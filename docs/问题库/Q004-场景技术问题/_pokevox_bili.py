# -*- coding: utf-8 -*-
"""Pokevox B站检索（WBI 签名版）+ Pokeball/LongStrafes 字幕"""
import sys, os, re, json, time, requests

BASE = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q004-场景技术问题\Pokevox快打检索"
os.makedirs(os.path.join(BASE, "字幕"), exist_ok=True)
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                  "Referer": "https://www.bilibili.com"})

# ---- WBI 签名 ----
import hashlib
from urllib.parse import urlencode
MIXIN = "9ca38c1e7f2a4b6d8e0f5a3c1b7d9e2f"  # 常用 mixin（若失效走 cookie 池接口）
def wbi_search(kw):
    try:
        r = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=15).json()
        img, sub = r["data"]["wbi_img"]["img_url"], r["data"]["wbi_img"]["sub_url"]
        img_key = img.rsplit("/", 1)[1].split(".")[0]
        sub_key = sub.rsplit("/", 1)[1].split(".")[0]
        key = "".join(sorted(img_key + sub_key))
        key = "".join(key[i] for i in MIXIN_INDICES)
    except Exception:
        key = None
    params = {"keyword": kw, "search_type": "video", "page": 1, "order": "totalrank",
              "duration": 0, "tids": 0, "page_size": 20}
    params["wts"] = int(time.time())
    q = urlencode(sorted(params.items()))
    if key:
        params["w_rid"] = hashlib.md5((q + key).encode()).hexdigest()
    r = s.get("https://api.bilibili.com/x/web-interface/wbi/search/type", params=params, timeout=15,
              headers={"Cookie": pool.get_cookie()}).json()
    if r.get("code") != 0:
        return None, r.get("message")
    return [x for x in r.get("data", {}).get("result", []) if x.get("type") == "video"], None

# mixin 交错的索引表（标准 33 键变换）
MIXIN_INDICES = [46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
                 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
                 61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
                 36, 20, 34, 44, 52]

QS = ["Pokevox", "pokevox", "LG56 kovaaks", "lowgravity56", "kovaaks 电枪 跟枪",
      "kovaak LG 高分", "quaker bot long strafes", "kovaaks 移动靶 秒杀",
      "kovaaks 大佬 跟枪", "kovaaks 转火 教学", "pokeball kovaaks"]
out, seen = [], set()
for q in QS:
    items, err = wbi_search(q)
    if items is None:
        print("[%s] 失败: %s" % (q, err)); continue
    print("[%s] %d" % (q, len(items)))
    for it in items:
        bv = it.get("bvid")
        if not bv or bv in seen: continue
        seen.add(bv)
        out.append({"kw": q, "bvid": bv, "title": re.sub("<[^>]+>", "", it.get("title", "")),
                    "author": it.get("author"), "play": it.get("play"),
                    "desc": (it.get("description") or "")[:150]})
print("去重", len(out))
for i, b in enumerate(out[:35]):
    print("#%d [%s] %s | %s | %s" % (i + 1, b["bvid"], b["title"][:52], b["author"], b["play"]))
json.dump(out, open(os.path.join(BASE, "b站搜索.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- 抓重点字幕 ----
def get_cid(bvid):
    r = s.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", timeout=20).json()
    return r["data"]["cid"] if r.get("code") == 0 else None

def sub_url(bvid, cid):
    r = s.get(f"https://api.bilibili.com/x/player/wbi/v2?bvid={bvid}&cid={cid}", timeout=20).json()
    subs = r.get("data", {}).get("subtitle", {}).get("subtitles", [])
    if not subs: return None
    subs.sort(key=lambda x: 0 if "zh" in x.get("lan", "") else 1)
    return subs[0].get("subtitle_url", "")

SELECTED = [
    ("rkVpuRwXqe4_placeholder", ""),  # 占位，B站重点单独列
]
# B站重点：从检索结果里挑标题含 pokevox/LG56/电枪/转火 的
KEYS = ["pokevox", "lg56", "lowgravity", "电枪", "转火", "跟枪", "kovaak", "练枪"]
prio = [b for b in out if any(k in (b["title"] + b["author"]).lower() for k in KEYS)][:12]
ok = 0
for b in prio:
    try:
        s.headers["Cookie"] = pool.get_cookie()
        cid = get_cid(b["bvid"])
        if not cid: print("  cid失败", b["bvid"]); continue
        u = sub_url(b["bvid"], cid)
        if not u: print("  无字幕", b["bvid"], b["title"][:30]); continue
        if u.startswith("//"): u = "https:" + u
        t = "\n".join(x["content"] for x in s.get(u, timeout=20).json().get("body", []))
        safe = re.sub(r'[\\/:*?"<>|]', "_", b["title"])[:60]
        open(os.path.join(BASE, "字幕", f"{b['bvid']}_{safe}.txt"), "w", encoding="utf-8").write(
            f"# {b['title']}\n# {b['bvid']} | {b['author']}\n\n" + t)
        ok += 1; print("  OK", b["bvid"], b["title"][:36], len(t))
    except Exception as e:
        print("  ERR", b["bvid"], e)
    time.sleep(1.5)
print("B站字幕 %d/%d" % (ok, len(prio)))
