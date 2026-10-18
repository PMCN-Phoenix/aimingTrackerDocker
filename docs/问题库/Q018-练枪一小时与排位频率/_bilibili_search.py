# -*- coding: utf-8 -*-
"""B站搜索：Q018 每天练枪 1 小时，多久打一次瓦（排位频率 / 生活平衡 / 持续进步）"""
import sys, json, time, hashlib, urllib.parse, requests, re, os
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
    img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
    mixin_key = "".join((img + sub)[i] for i in MIXIN)[:32]
    params["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(params.items()))
    params["w_rid"] = hashlib.md5((q + mixin_key).encode()).hexdigest()
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
    "排位频率": ["每天打几把排位", "一周打几次排位", "排位 频率", "一天几把 上分",
             "每天打一把 排位", "排位 打多少把", "上分 每天 几局"],
    "练枪一小时": ["每天练枪一小时", "练枪 多久 有用", "练枪 一小时 够吗",
              "每天练枪 多久", "练枪 时间 安排", "练枪 多久 上分"],
    "练枪vs实战": ["练枪 实战 比例", "只练枪 不打排位", "练枪 不上分",
              "练枪 转化 实战", "死斗 排位 区别", "aimlab 有用吗 瓦"],
    "时间预算": ["上班族 练枪", "学生 练枪 时间", "时间少 怎么练枪",
             "每天 一小时 上分", "练枪 时间管理", "瓦 上分 计划"],
    "进步节奏": ["瓦 上分 节奏", "上分 周期", "段位 提升 时间", "瓦 训练计划",
             "瓦 怎么练 进步快", "aim训练 计划 瓦"],
    "反面意见": ["排位 打太多", "排位 疲劳", "上分 焦虑", "打瓦 上瘾",
             "练枪 没用", "练枪 浪费时间"],
}

os.makedirs("B站原始数据", exist_ok=True)
allv, seen = [], set()

for g, kws in groups.items():
    print(f"\n## {g}")
    for kw in kws:
        try:
            res = search(kw)
        except Exception as e:
            print(f"  {kw}: ERR {e}")
            time.sleep(2)
            continue
        n = 0
        for it in res:
            bv = it.get("bvid")
            if not bv or bv in seen:
                continue
            seen.add(bv)
            dur = it.get("duration", "")
            play = it.get("play", 0)
            if isinstance(play, str):
                play = 0
            allv.append({"bvid": bv, "title": re.sub(r"<[^>]+>", "", it.get("title", "")),
                         "author": it.get("author", ""), "play": play,
                         "duration": dur, "pubdate": it.get("pubdate", 0),
                         "group": g, "keyword": kw,
                         "desc": re.sub(r"<[^>]+>", "", it.get("description", ""))[:200]})
            n += 1
        print(f"  {kw}: +{n}")
        time.sleep(1.1)

json.dump(allv, open("B站原始数据/搜索清单.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\n总去重 {len(allv)} 条")

# 粗筛：标题/简介命中主题词
kw_hit = ["排位", "上分", "练枪", "频率", "每天", "每周", "时间", "计划", "进步",
          "段位", "训练", "实战", "局", "把", "小时", "分钟"]
cand = [v for v in allv if any(k in v["title"] for k in kw_hit)]
cand.sort(key=lambda x: -x["play"])
print(f"粗筛 {len(cand)} 条，播放前 45：")
for v in cand[:45]:
    print("%8d %-12s %-7s %s" % (v["play"], v["bvid"], v["duration"], v["title"][:52]))
json.dump(cand, open("B站原始数据/粗筛候选.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
