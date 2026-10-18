# -*- coding: utf-8 -*-
"""B站评论抓取：Q016（限速，风控则记录跳过）"""
import sys, json, time, requests, os, hashlib, urllib.parse
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

def sign(params):
    s.headers["Cookie"] = pool.get_cookie()
    nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=15).json()
    wbi = nav["data"]["wbi_img"]
    img = wbi["img_url"].rsplit("/",1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/",1)[-1].split(".")[0]
    mixin_key = "".join((img+sub)[i] for i in MIXIN)[:32]
    params["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(params.items()))
    params["w_rid"] = hashlib.md5((q+mixin_key).encode()).hexdigest()
    return params

def get_aid(bvid):
    r = s.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", timeout=20).json()
    if r.get("code") != 0:
        return None
    return r["data"]["aid"]

def comments(aid, pages=2):
    out = []
    for pn in range(1, pages+1):
        p = sign({"oid": aid, "type": 1, "pn": pn, "ps": 20, "sort": 2, "web_location": "1315875"})
        r = s.get("https://api.bilibili.com/x/v2/reply/wbi/main", params=p, timeout=25)
        if r.status_code == 412 or '"code":-412' in r.text:
            pool.report_412()
            print("   412 风控，跳过")
            break
        j = r.json()
        if j.get("code") != 0:
            print(f"   code={j.get('code')} {j.get('message')}")
            break
        pool.report_success()
        reps = j.get("data", {}).get("replies") or []
        if not reps:
            break
        for c in reps:
            out.append({
                "user": c["member"]["uname"],
                "like": c["like"],
                "content": c["content"]["message"],
                "rcount": c["rcount"],
                "sub": [{"user": rr["member"]["uname"], "like": rr["like"], "content": rr["content"]["message"]}
                        for rr in (c.get("replies") or [])][:5],
            })
        time.sleep(2)
    return out

TARGETS = [
    ("BV1ojmVYxEv1", "熬夜/放纵对瞄准的影响（个人实验）"),
    ("BV13XYT6dEGG", "别疲劳练枪 状态差练了白搭"),
    ("BV1dz421y72z", "为什么越打状态越差"),
    ("BV1qt421a7Zu", "练枪是自我感动的偷懒"),
]

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "B站原始数据")
os.makedirs(out_dir, exist_ok=True)
allc = {}
for bvid, title in TARGETS:
    print(f"== {bvid} {title}")
    aid = get_aid(bvid)
    if not aid:
        print("  aid 获取失败")
        continue
    cs = comments(aid, pages=2)
    cs.sort(key=lambda x: x["like"], reverse=True)
    allc[bvid] = {"title": title, "count": len(cs), "comments": cs}
    print(f"  {len(cs)} 条")
    time.sleep(2)

with open(os.path.join(out_dir, "评论.json"), "w", encoding="utf-8") as f:
    json.dump(allc, f, ensure_ascii=False, indent=2)
print(f"\n总评论 {sum(v['count'] for v in allc.values())} 条 → 评论.json")
