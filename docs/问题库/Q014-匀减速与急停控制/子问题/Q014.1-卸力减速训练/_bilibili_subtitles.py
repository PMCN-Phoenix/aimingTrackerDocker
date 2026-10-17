# -*- coding: utf-8 -*-
"""抓取精选B站视频字幕：卸力减速（途中泄力）怎么训练（Q014.1）"""
import sys, json, time, hashlib, urllib.parse, requests, re, os
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

def get_cid(bvid):
    r = s.get(f"https://www.bilibili.com/video/{bvid}/", timeout=20)
    m = re.search(r'window\.__INITIAL_STATE__=(.*?);\(function', r.text, re.S)
    if not m:
        m = re.search(r'window\.__INITIAL_STATE__=(.*?);\s*</script>', r.text, re.S)
    d = json.loads(m.group(1))
    v = d['videoData']
    return v['aid'], v['cid'], v['title']

def get_subtitle(bvid, cid):
    cookie = pool.get_cookie()
    s.headers["Cookie"] = cookie
    nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=15).json()
    wbi = nav["data"]["wbi_img"]
    img = wbi["img_url"].rsplit("/",1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/",1)[-1].split(".")[0]
    mixin_key = "".join((img+sub)[i] for i in MIXIN)[:32]
    p = {'bvid': bvid, 'cid': cid, 'wts': str(int(time.time()))}
    q = urllib.parse.urlencode(sorted(p.items()))
    p['w_rid'] = hashlib.md5((q+mixin_key).encode()).hexdigest()
    r = s.get("https://api.bilibili.com/x/player/wbi/v2", params=p, timeout=20)
    subs = r.json()['data']['subtitle']['subtitles']
    if not subs:
        return None
    sub_url = subs[0]['subtitle_url']
    if sub_url.startswith('//'):
        sub_url = 'https:' + sub_url
    r2 = s.get(sub_url, timeout=20)
    return r2.json()

targets = [
    ("BV1A9KpzTEHL", "VEI_J-张力控制全攻略48万播放"),
    ("BV1P7SvBaEee", "xen2-紧握鼠标是错的吗利用张力进阶（中字）"),
    ("BV1fKqGB4Eds", "xen2-动作分离与发力模式（中字）"),
    ("BV1Nfby6kEgQ", "芝士A菌-张力控制不等于无脑放松（反面意见）"),
    ("BV1XPXYBVEzm", "MYCRUSH二哥-FPS科学控鼠发力短TTK"),
    ("BV1dGVNzdEJL", "KAUS666-张力管理搬运机翻"),
    ("BV1pMga6WEaq", "花猫-131握法无名指辅助发力"),
]

out_dir = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q014-匀减速与急停控制\子问题\Q014.1-卸力减速训练\B站原始数据\字幕"
os.makedirs(out_dir, exist_ok=True)

results = []
for bvid, label in targets:
    try:
        aid, cid, title = get_cid(bvid)
        sub = get_subtitle(bvid, cid)
        safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)[:80]
        if sub:
            body = "\n".join(
                f"[{int(float(e['from']))//60:02d}:{int(float(e['from']))%60:02d}] {e['content']}"
                for e in sub.get("body", [])
            )
            path = os.path.join(out_dir, f"{bvid}_{safe_title}.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"标题: {title}\nBV: {bvid}\n{'='*40}\n\n{body}\n")
            n = len(sub.get("body", []))
            print(f"✓ {bvid} {label} -> {n} 段字幕")
            results.append({"bvid": bvid, "label": label, "title": title, "segments": n, "ok": True})
        else:
            print(f"✗ {bvid} {label} -> 无AI字幕")
            results.append({"bvid": bvid, "label": label, "title": title, "ok": False, "reason": "no_subtitle"})
    except Exception as e:
        print(f"✗ {bvid} {label} -> 错误: {e}")
        results.append({"bvid": bvid, "label": label, "ok": False, "reason": str(e)})
    time.sleep(2)

with open(os.path.join(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q014-匀减速与急停控制\子问题\Q014.1-卸力减速训练\B站原始数据", "抓取记录.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("\n完成:", sum(1 for r in results if r["ok"]), "/", len(targets))
