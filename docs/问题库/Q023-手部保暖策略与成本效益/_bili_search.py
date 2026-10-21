# -*- coding: utf-8 -*-
"""B站搜索：手部保暖策略与成本效益（Q023）"""
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
    "机制与体感": ["冬天打游戏手冷", "手冷 影响 瞄准", "手冷 手感 游戏", "冬天 练枪 手感",
               "手指僵硬 游戏", "低温 反应速度", "手冷 准度 下降", "手冰凉 鼠标",
               "冬天 FPS 手感"],
    "装备实测": ["暖手宝 打游戏", "加热鼠标垫 实测", "电加热手套 打游戏", "暖风机 打游戏",
              "加热桌垫 缺点", "半指手套 打游戏", "暖手宝 电竞", "加热鼠标垫 玻璃",
              "USB加热手套 测评", "暖手宝 测评 缺点"],
    "职业与技巧": ["职业选手 暖手", "电竞 手部保暖", "冬天 排位 手冷", "暖手 技巧 游戏",
               "手冷 搓手 热身", "赛前 热身 手", "游戏 手部 血液循环", "冬天 训练室 温度"],
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
    ("暖手宝", 15), ("加热鼠标垫", 15), ("加热手套", 14), ("电加热", 13), ("手冷", 13),
    ("保暖", 12), ("实测", 12), ("测评", 11), ("手套", 11), ("鼠标垫", 10),
    ("暖风机", 10), ("手感", 9), ("瞄准", 9), ("FPS", 9), ("温度", 8),
    ("冬天", 8), ("价格", 8), ("性价比", 9), ("缺点", 8), ("职业", 7),
    ("电竞", 7), ("游戏", 6), ("鼠标", 7), ("手指", 8), ("僵硬", 8),
    ("冰", 6), ("暖脚", 5), ("桌垫", 8), ("瓦", 4),
]
def score(v):
    t = ((v["title"] or "") + " " + (v.get("desc") or "")).lower()
    sc = sum(w for k, w in W if k.lower() in t)
    if len(v["_kw"]) >= 2: sc += 5
    if len(v["_kw"]) >= 3: sc += 3
    p = v.get("play") or 0
    sc += 4 if p > 100000 else 3 if p > 30000 else 2 if p > 5000 else 1 if p > 1000 else -1
    return sc

results = sorted(all_results.values(), key=score, reverse=True)
for i, v in enumerate(results[:30]):
    print(f"  #{i+1} [{score(v)}分] {v['title'][:52]} | {v['author']} | 播放={v['play']} | {v['bvid']}")

out_dir = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q023-手部保暖策略与成本效益\B站原始数据"
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "搜索清单.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n总计去重后: {len(results)} 个视频")
print(f"已保存到: {out_dir}\\搜索清单.json")
