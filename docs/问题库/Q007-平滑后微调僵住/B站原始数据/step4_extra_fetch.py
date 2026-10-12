# -*- coding: utf-8 -*-
"""Step4: 追加场景视频抓信息+字幕"""
import sys, os, re, json, time, hashlib, urllib.parse
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool
import requests

OUT_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q007-平滑后微调僵住\B站原始数据"
SUB_DIR = os.path.join(OUT_DIR, "字幕")

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]
PROXIES = {"http": "http://127.0.0.1:7892", "https": "http://127.0.0.1:7892"}

EXTRA_SELECTED = [
    "BV1tq4y1A7yA",  # 5分钟化身预瞄之神 (46万,大东彦)
    "BV1fd4y1R7kd",  # 无畏契约所有Peek方式汇总 (43万,大东彦)
    "BV1MY4y1H79Z",  # Valorant最全急停教学 (63万,大东彦)
    "BV1UBTKzKEDf",  # 预瞄不是一切，微调才是大拉击杀效率的关键 (26万,大东彦)
    "BV16eaA6bE9F",  # 控鼠僵硬卡手？一个视频讲透拉枪 (2.4万,晨曜cheyo)
    "BV1o87S62Ezw",  # 开枪节奏就是二次调整能力和移动蹲操作结合 (6670)
]

def make_session(pool):
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    })
    s.proxies.update(PROXIES)
    s.headers["Cookie"] = pool.get_cookie()
    return s

def get_wbi_keys(s):
    nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=20).json()
    wbi = nav["data"]["wbi_img"]
    img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
    return "".join((img + sub)[i] for i in MIXIN)[:32]

def sign(p, mixin):
    p = dict(p); p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q + mixin).encode()).hexdigest()
    return p

def fetch_info(s, pool, bvid):
    for attempt in range(3):
        try:
            r = s.get(f"https://www.bilibili.com/video/{bvid}/", timeout=25)
            t = r.text
            m = (re.search(r"window\.__INITIAL_STATE__=(.*?);\(function", t, re.S)
                 or re.search(r"window\.__INITIAL_STATE__=(.*?);\s*</script>", t, re.S))
            if not m: return None
            v = json.loads(m.group(1))["videoData"]
            pool.report_success()
            return {"aid": v.get("aid"), "cid": v.get("cid"), "title": v.get("title"),
                    "owner": (v.get("owner") or {}).get("name"), "duration": v.get("duration"),
                    "desc": (v.get("desc") or "")[:800]}
        except Exception as e:
            print(f"  [!] {bvid}: {e}"); time.sleep(3)
    return None

def fetch_sub(s, pool, mixin, bvid, cid):
    q = sign({"bvid": bvid, "cid": str(cid), "web_location": "333.1007"}, mixin)
    for attempt in range(4):
        try:
            d = s.get("https://api.bilibili.com/x/player/wbi/v2", params=q,
                      headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"}, timeout=20).json()
            subs = ((d.get("data") or {}).get("subtitle") or {}).get("subtitles") or []
            if not subs:
                if d.get("code") == -412:
                    pool.report_412(); s.headers["Cookie"] = pool.get_cookie(); time.sleep(3); continue
                return None
            pool.report_success()
            pick = next((x for pref in ["zh-Hans","zh-CN","zh","ai-zh"] for x in subs if x.get("lan") == pref), subs[0])
            u = pick.get("subtitle_url") or ""
            if not u: time.sleep(3); continue
            if u.startswith("//"): u = "https:" + u
            body = s.get(u, headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"}, timeout=25).json()["body"]
            return {"lan": pick.get("lan"), "body": body}
        except Exception as e:
            print(f"  [!] sub: {e}"); time.sleep(3)
    return None

def main():
    pool = BiliCookiePool()
    s = make_session(pool)
    mixin = get_wbi_keys(s)

    # 加载已有精选列表
    sel_path = os.path.join(OUT_DIR, "精选列表.json")
    with open(sel_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    for i, bvid in enumerate(EXTRA_SELECTED):
        print(f"\n[{i+1}/{len(EXTRA_SELECTED)}] {bvid}")
        info = fetch_info(s, pool, bvid)
        if not info:
            print("  [!] 跳过"); continue
        print(f"  {info['title'][:50]} | {info['owner']} | dur={info['duration']}")
        entry = dict(info); entry["bvid"] = bvid; entry["is_extra"] = True

        if info.get("cid"):
            sub = fetch_sub(s, pool, mixin, bvid, info["cid"])
            if sub:
                entry["subtitle_lan"] = sub["lan"]
                entry["subtitle_segments"] = len(sub["body"])
                entry["subtitle_coverage"] = round(sub["body"][-1]["to"]/info["duration"], 3) if info["duration"] and sub["body"] else 0
                with open(os.path.join(SUB_DIR, f"{bvid}.json"), "w", encoding="utf-8") as f:
                    json.dump({"bvid": bvid, "title": info["title"], "owner": info["owner"],
                               "duration": info["duration"], "lan": sub["lan"], "body": sub["body"]}, f, ensure_ascii=False, indent=2)
                with open(os.path.join(SUB_DIR, f"{bvid}.txt"), "w", encoding="utf-8") as f:
                    f.write(f"# {info['title']} | UP: {info['owner']} | {bvid}\n\n")
                    for seg in sub["body"]:
                        m, sec = divmod(int(seg["from"]), 60)
                        f.write(f"[{m:02d}:{sec:02d}] {seg['content']}\n")
                print(f"  字幕: {len(sub['body'])}段, 覆盖{entry['subtitle_coverage']*100:.1f}%")
            else:
                entry["subtitle_lan"] = None
                print("  字幕: 无")
            time.sleep(1.5)
        results[bvid] = entry

    with open(sel_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] 追加完成, 精选列表共 {len(results)} 个视频")

if __name__ == "__main__":
    main()
