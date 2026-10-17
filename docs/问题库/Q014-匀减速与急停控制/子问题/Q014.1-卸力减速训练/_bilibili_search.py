# -*- coding: utf-8 -*-
"""B站搜索：卸力减速（途中泄力）怎么训练（Q014.1 训练专研）"""
import sys, json, time, hashlib, urllib.parse, requests, re, os
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

def sign(params):
    cookie = pool.get_cookie()
    s.headers["Cookie"] = cookie
    nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=15).json()
    wbi = nav["data"]["wbi_img"]
    img = wbi["img_url"].rsplit("/",1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/",1)[-1].split(".")[0]
    mixin_key = "".join((img+sub)[i] for i in MIXIN)[:32]
    params["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(params.items()))
    params["w_rid"] = hashlib.md5((q+mixin_key).encode()).hexdigest()
    return params

def search(kw, page=1):
    p = sign({"search_type": "video", "keyword": kw, "page": page, "page_size": 30})
    r = s.get("https://api.bilibili.com/x/web-interface/wbi/search/type", params=p, timeout=25)
    res = r.json()
    if res.get("code") != 0:
        print(f"  code={res.get('code')} msg={res.get('message')}")
        return []
    return res["data"].get("result", [])

groups = {
    "卸力训练法": ["卸力 训练", "泄力 瞄准", "放松 瞄准 训练", "肌肉放松 拉枪", "瞄准 张力 释放", "握鼠标 力度 训练"],
    "发力控制": ["瞄准 发力 控制", "鼠标 握压", "推鼠标 拉鼠标", "前臂 发力 瞄准", "点击 发力 节奏"],
    "慢速与感知": ["慢速 练枪", "降速 练习 瞄准", "摩擦力 感知 鼠标", "本体感觉 瞄准", "肌肉记忆 练枪 方法"],
    "场景与课程": ["kovaak smoothness 训练", "smoothbot", "voltaic 平滑", "瓦罗兰特 瞄准教学 放松", "无畏契约 拉枪 发力"],
}

all_results = {}
for gname, keywords in groups.items():
    print(f"\n=== 分组: {gname} ===")
    for kw in keywords:
        try:
            res = search(kw)
            print(f"  [{kw}] {len(res)}条")
            for v in res:
                bvid = v.get("bvid", "")
                if bvid and bvid not in all_results:
                    title = re.sub(r"<[^>]+>", "", v.get("title", ""))
                    all_results[bvid] = {
                        "bvid": bvid,
                        "title": title,
                        "author": v.get("author", ""),
                        "play": v.get("play", 0),
                        "duration": v.get("duration", ""),
                        "pubdate": v.get("pubdate", 0),
                        "desc": v.get("description", "")[:200],
                        "_kw": [kw],
                        "_group": gname,
                    }
                elif bvid in all_results:
                    if kw not in all_results[bvid]["_kw"]:
                        all_results[bvid]["_kw"].append(kw)
        except Exception as e:
            print(f"  [{kw}] 错误: {e}")
        time.sleep(1.5)

W = [
    ("卸力", 16), ("泄力", 16), ("放松", 14), ("发力", 12), ("张力", 11),
    ("握压", 11), ("力度", 10), ("减速", 10), ("训练", 8), ("练", 6),
    ("smooth", 9), ("smoothness", 10), ("平滑", 8), ("流畅", 8), ("relax", 8),
    ("tension", 9), ("握法", 7), ("手腕", 6), ("前臂", 6), ("手臂", 5),
    ("拉枪", 6), ("定位", 5), ("跟枪", 5), ("瞄准", 4), ("kovaak", 6), ("慢", 5),
]
def score(v):
    t = ((v["title"] or "") + " " + (v.get("desc") or "")).lower()
    s = sum(w for k, w in W if k.lower() in t)
    if len(v["_kw"]) >= 2: s += 5
    if len(v["_kw"]) >= 3: s += 3
    if v.get("duration"):
        try:
            mm, ss = v["duration"].split(":")
            total = int(mm)*60 + int(ss)
        except Exception:
            total = 0
        if 180 <= total <= 900: s += 6      # 3-15 分钟教学最可能是干货
        elif total < 60: s -= 8             # 纯剪辑
    return s

for v in all_results.values():
    v["score"] = score(v)

ranked = sorted(all_results.values(), key=lambda x: -x["score"])
out = {
    "检索时间": time.strftime("%Y-%m-%d %H:%M:%S"),
    "主题": "卸力减速（途中泄力）怎么训练（Q014.1）",
    "分组关键词": groups,
    "去重总数": len(ranked),
    "视频": ranked,
}
with open("B站原始数据/搜索清单.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print(f"\n去重总数: {len(ranked)}")
print("\nTOP 22:")
for v in ranked[:22]:
    print(f"  {v['score']:>3} | {v['bvid']} | {v['play']:>7} | {v['title'][:52]} | {v['author']}")
